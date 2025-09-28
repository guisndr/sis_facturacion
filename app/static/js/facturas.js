function initFactura() {
    const detallesContainer = document.getElementById('items');
    
    if (!detallesContainer) {
        console.log('Contenedor de items de factura no encontrado');
        return;
    }
    
    // Leemos los precios enviados por el servidor (JSON embebido en la página)
    let PRECIOS_PRODUCTO = {};
    const preciosEl = document.getElementById('precios-data');
    if (preciosEl && preciosEl.textContent) {
        try {
            PRECIOS_PRODUCTO = JSON.parse(preciosEl.textContent) || {};
        } catch (e) {
            console.warn('No se pudo parsear PRECIOS_PRODUCTO:', e);
        }
    }
    
    let itemIndex = detallesContainer.querySelectorAll('.item').length;  // Cantidad de filas actuales

    function addItemAfter(afterItem) {
        const templateItem = detallesContainer.querySelector('.item');
        if (!templateItem) {
            console.log('No se encontró un item template para clonar');
            return;
        }
        const newItem = templateItem.cloneNode(true);  // Usamos la primera fila como base

        // Actualizamos name, id y los for de los labels al nuevo índice
        newItem.querySelectorAll('input, select, label').forEach(el => {
            if (el.name) {
                const m = el.name.match(/items-(\d+)/);
                const oldIdx = m ? m[1] : '0';
                el.name = el.name.replace(`items-${oldIdx}`, `items-${itemIndex}`);
            }
            if (el.id) {
                const m2 = el.id.match(/items-(\d+)/);
                const oldIdx2 = m2 ? m2[1] : '0';
                el.id = el.id.replace(`items-${oldIdx2}`, `items-${itemIndex}`);
            }
            if (el.tagName === 'LABEL' && el.htmlFor) {
                const m3 = el.htmlFor.match(/items-(\d+)/);
                const oldIdx3 = m3 ? m3[1] : '0';
                el.htmlFor = el.htmlFor.replace(`items-${oldIdx3}`, `items-${itemIndex}`);
            }
        });

        // Limpiamos valores del nuevo ítem
        const selectProducto = newItem.querySelector('[name*="producto_id"]');
        if (selectProducto) selectProducto.selectedIndex = 0; // Opción por defecto
        const cantidadInput = newItem.querySelector('[name*="cantidad"]');
        if (cantidadInput) cantidadInput.value = '';
        const precioInput = newItem.querySelector('[name*="precio_unitario"]');
        if (precioInput) precioInput.value = '';
        const subtotalInput = newItem.querySelector('[name*="subtotal"]');
        if (subtotalInput) subtotalInput.value = '';

        // Ocultamos "Agregar otro ítem" hasta elegir un producto
        const addBtn = newItem.querySelector('.add-after');
        if (addBtn) addBtn.classList.add('d-none');

        // Insertamos la nueva fila debajo de la actual
        afterItem.insertAdjacentElement('afterend', newItem);
        itemIndex++;
        renumberItems();
        updateTotal();
        return newItem;
    }

    function renumberItems() {
        const items = Array.from(detallesContainer.querySelectorAll('.item'));
        items.forEach((item, idx) => {
            item.querySelectorAll('input, select, label').forEach(el => {
                if (el.name) {
                    el.name = el.name.replace(/items-\d+/, `items-${idx}`);
                }
                if (el.id) {
                    el.id = el.id.replace(/items-\d+/, `items-${idx}`);
                }
                if (el.tagName === 'LABEL' && el.htmlFor) {
                    el.htmlFor = el.htmlFor.replace(/items-\d+/, `items-${idx}`);
                }
            });
        });
        // Ajustamos el siguiente índice disponible
        itemIndex = items.length;
        // Mostramos/ocultamos el botón eliminar según cuántas filas haya
        updateRemoveButtonsVisibility();
    }

    function updateRemoveButtonsVisibility() {
        const items = detallesContainer.querySelectorAll('.item');
        const showRemove = items.length > 1;
        items.forEach(item => {
            const btnRemove = item.querySelector('.remove-item');
            if (btnRemove) {
                btnRemove.classList.toggle('d-none', !showRemove);
            }
        });
    }

    // Click: agregar/eliminar filas
    detallesContainer.addEventListener('click', function(e) {
        if (e.target.classList.contains('add-after')) {
            e.preventDefault();
            const currentItem = e.target.closest('.item');
            addItemAfter(currentItem);
        } else if (e.target.classList.contains('remove-item')) {
            e.preventDefault();
            const currentItem = e.target.closest('.item');
            if (currentItem) {
                currentItem.remove();
                renumberItems();
                updateTotal();
            }
        }
    });
    
    // Cuando cambia cantidad o precio, recalculamos
    detallesContainer.addEventListener('input', function(e) {
        if (e.target.name.includes('cantidad') || e.target.name.includes('precio_unitario')) {
            // Si cambia cantidad, asegurar que no supere el stock del producto seleccionado
            if (e.target.name.includes('cantidad')) {
                const item = e.target.closest('.item');
                const sel = item.querySelector('[name*="producto_id"]');
                const selected = sel ? sel.options[sel.selectedIndex] : null;
                const stock = parseInt(selected?.dataset?.stock || '0', 10);
                const qty = parseInt(e.target.value || '0', 10);
                if (Number.isFinite(stock) && stock >= 0 && qty > stock) {
                    e.target.value = stock;
                } else if (qty < 1) {
                    e.target.value = 1;
                }
            }
            updateTotal();
        }
    });
    
    // Al elegir producto, completamos precio, mostramos stock y limitamos cantidad
    detallesContainer.addEventListener('change', function(e) {
        if (e.target.name.includes('producto_id')) {
            const item = e.target.closest('.item');
            const selected = e.target.options[e.target.selectedIndex];
            // Tomamos el precio del option o del mapa de precios
            let precio = parseFloat(selected?.dataset?.precio || 0);
            if ((!precio || isNaN(precio)) && PRECIOS_PRODUCTO) {
                const pid = e.target.value;
                const p2 = PRECIOS_PRODUCTO[pid];
                if (p2) precio = parseFloat(p2) || 0;
            }
            const precioInput = item.querySelector('[name*="precio_unitario"]');
            const qtyInput = item.querySelector('[name*="cantidad"]');
            const stockDisplay = item.querySelector('.stock-display');
            const stock = parseInt(selected?.dataset?.stock || '0', 10);
            if (precioInput) {
                precioInput.value = precio.toFixed(2);
            }
            // Si la cantidad está vacía o 0, dejamos 1 por defecto
            if (qtyInput && (!qtyInput.value || parseInt(qtyInput.value) <= 0)) {
                qtyInput.value = 1;
            }
            // Mostramos el stock y limitamos la cantidad a ese tope
            if (stockDisplay) {
                stockDisplay.textContent = Number.isFinite(stock) ? `Stock disponible: ${stock}` : '';
            }
            if (qtyInput) {
                if (Number.isFinite(stock)) {
                    qtyInput.setAttribute('max', stock);
                    const currentQty = parseInt(qtyInput.value || '0', 10);
                    if (currentQty > stock) {
                        qtyInput.value = stock;
                    }
                } else {
                    qtyInput.removeAttribute('max');
                }
            }
            // Habilitamos el botón "Agregar otro ítem" en esta fila
            const addBtn = item.querySelector('.add-after');
            if (addBtn) addBtn.classList.remove('d-none');
            updateTotal();
        }
    });
    
    // Calcula subtotales y total general
    function updateTotal() {
        let total = 0;
        detallesContainer.querySelectorAll('.item').forEach(item => {
            const qty = parseInt(item.querySelector('[name*="cantidad"]').value) || 0;
            const price = parseFloat(item.querySelector('[name*="precio_unitario"]').value) || 0;
            const productoId = item.querySelector('[name*="producto_id"]')?.value || '';
            const subtotal = qty * price;
            item.querySelector('[name*="subtotal"]').value = subtotal.toFixed(2);
            if (productoId && qty > 0) {
                total += subtotal;
            }
        });
        
        document.getElementById('total').textContent = total.toFixed(2);
    }
    
    // Antes de enviar: quitamos filas vacías, completamos precios y renumeramos
    const form = document.getElementById('facturaForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            const items = Array.from(detallesContainer.querySelectorAll('.item'));
            let validCount = 0;
            items.forEach(item => {
                const sel = item.querySelector('[name*="producto_id"]');
                const pid = sel ? sel.value : '';
                const qtyInput = item.querySelector('[name*="cantidad"]');
                const priceInput = item.querySelector('[name*="precio_unitario"]');
                // Autocompletar precio si falta
                if (pid && priceInput && (!priceInput.value || parseFloat(priceInput.value) <= 0)) {
                    const precio = PRECIOS_PRODUCTO && PRECIOS_PRODUCTO[pid] ? parseFloat(PRECIOS_PRODUCTO[pid]) : 0;
                    if (precio > 0) priceInput.value = precio.toFixed(2);
                }
                const qty = qtyInput ? parseInt(qtyInput.value) : 0;
                if (!pid || pid === '0' || !qty || qty <= 0) {
                    // Quitamos filas vacías para evitar errores en el servidor
                    item.remove();
                } else {
                    validCount++;
                }
            });
            renumberItems();
            updateTotal();
            if (validCount === 0) {
                e.preventDefault();
                alert('Agregá al menos un item con producto y cantidad válida.');
            }
        });
    }

    updateTotal();  // Cálculo inicial
    updateRemoveButtonsVisibility();

    // Si volvemos de un error, inicializamos el texto de stock y límites
    detallesContainer.querySelectorAll('.item').forEach(item => {
        const sel = item.querySelector('[name*="producto_id"]');
        if (sel && sel.value) {
            const selected = sel.options[sel.selectedIndex];
            const stock = parseInt(selected?.dataset?.stock || '0', 10);
            const stockDisplay = item.querySelector('.stock-display');
            if (stockDisplay) {
                stockDisplay.textContent = Number.isFinite(stock) ? `Stock disponible: ${stock}` : '';
            }
            const qtyInput = item.querySelector('[name*="cantidad"]');
            if (qtyInput && Number.isFinite(stock)) {
                qtyInput.setAttribute('max', stock);
                const qty = parseInt(qtyInput.value || '0', 10);
                if (qty > stock) qtyInput.value = stock;
                if (qty < 1) qtyInput.value = 1;
            }
        }
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFactura);
} else {
    initFactura();
}