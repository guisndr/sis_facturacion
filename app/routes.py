from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_required, current_user
from datetime import datetime
from . import db
from .models import Cliente, Producto, Factura, DetalleFactura
from .forms import ClienteForm, ClienteCreateForm, ProductoForm, FacturaForm, ReporteForm
from functools import wraps

main_bp = Blueprint("main", __name__)


def admin_required(f):
    """Permite entrar solo a administradores."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if (not current_user.is_authenticated) or (not getattr(current_user, "is_admin", False)):
            return abort(403)
        return f(*args, **kwargs)
    return wrapper

@main_bp.route("/")
@login_required
def index():
    """Redirige al listado de facturas"""
    return redirect(url_for('main.listar_facturas'))

@main_bp.route("/clientes")
@login_required
@admin_required
def listar_clientes():
    clientes = Cliente.query.all()
    return render_template("clientes/listar.html", clientes=clientes)

@main_bp.route("/clientes/nuevo", methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_cliente():
    form = ClienteCreateForm()
    if form.validate_on_submit():
        cliente = Cliente(
            nombre=form.nombre.data,
            direccion=form.direccion.data,
            telefono=form.telefono.data,
            email=form.email.data,
        )
        cliente.set_password(form.password.data)
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente creado', 'success')
        return redirect(url_for('main.listar_clientes'))
    return render_template("clientes/form.html", form=form, titulo="Nuevo Cliente")

@main_bp.route("/clientes/editar/<int:id>", methods=['GET', 'POST'])
@login_required
@admin_required
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    form = ClienteForm(obj=cliente)
    if form.validate_on_submit():
        cliente.nombre = form.nombre.data
        cliente.direccion = form.direccion.data
        cliente.telefono = form.telefono.data
        cliente.email = form.email.data
        db.session.commit()
        flash('Cliente actualizado', 'success')
        return redirect(url_for('main.listar_clientes'))
    return render_template("clientes/form.html", form=form, titulo="Editar Cliente")

@main_bp.route("/clientes/eliminar/<int:id>", methods=['GET'])
@login_required
@admin_required
def confirmar_eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    return render_template("clientes/eliminar.html", cliente=cliente)

@main_bp.route("/clientes/eliminar/<int:id>", methods=['POST'])
@login_required
@admin_required
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    try:
        if cliente.facturas:
            flash('No se puede eliminar el cliente porque tiene facturas asociadas', 'danger')
            return redirect(url_for('main.listar_clientes'))

        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente eliminado correctamente', 'success')
        return redirect(url_for('main.listar_clientes'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error al eliminar cliente {id}: {str(e)}')
        flash('Error al eliminar el cliente', 'danger')
        return redirect(url_for('main.listar_clientes'))

@main_bp.route("/productos")
@login_required
@admin_required
def listar_productos():
    productos = Producto.query.all()
    return render_template("productos/listar.html", productos=productos)

@main_bp.route("/productos/nuevo", methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        producto = Producto(
            descripcion=form.descripcion.data,
            precio=float(form.precio.data) if form.precio.data is not None else 0.0,
            stock=form.stock.data if form.stock.data is not None else 0,
        )
        db.session.add(producto)
        db.session.commit()
        flash('Producto creado', 'success')
        return redirect(url_for('main.listar_productos'))
    return render_template("productos/form.html", form=form, titulo="Nuevo Producto")

@main_bp.route("/productos/editar/<int:id>", methods=['GET', 'POST'])
@login_required
@admin_required
def editar_producto(id):
    producto = Producto.query.get_or_404(id)
    form = ProductoForm(obj=producto)
    if form.validate_on_submit():
        form.populate_obj(producto)
        db.session.commit()
        flash('Producto actualizado', 'success')
        return redirect(url_for('main.listar_productos'))
    return render_template("productos/form.html", form=form, titulo="Editar Producto")

@main_bp.route("/productos/eliminar/<int:id>", methods=['GET'])
@login_required
@admin_required
def confirmar_eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    return render_template("productos/eliminar.html", producto=producto)

@main_bp.route("/productos/eliminar/<int:id>", methods=['POST'])
@login_required
@admin_required
def eliminar_producto(id):
    current_app.logger.info(f"[POST] Solicitud de eliminación de producto ID={id}")
    producto = Producto.query.get_or_404(id)
    try:
        db.session.delete(producto)
        db.session.commit()
        current_app.logger.info(f"Producto ID={id} eliminado correctamente")
        flash('Producto eliminado correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error al eliminar producto {id}: {str(e)}', exc_info=True)
        flash('Error al eliminar el producto', 'danger')
    return redirect(url_for('main.listar_productos'))

@main_bp.route("/facturas")
@login_required
def listar_facturas():
    if getattr(current_user, "is_admin", False):
        facturas = Factura.query.all()
    else:
        facturas = Factura.query.filter(Factura.id_cliente == current_user.id).all()
    return render_template("facturas/listar.html", facturas=facturas)

@main_bp.route("/facturas/nueva", methods=['GET', 'POST'])
@login_required
@admin_required
def nueva_factura():
    clientes = [(c.id, c.nombre) for c in Cliente.query.all()]
    clientes_choices = [(0, 'Seleccione un cliente')] + clientes
    productos = Producto.query.all()
    productos_choices = [(p.id, f"{p.descripcion} (${p.precio})") for p in productos]
    form = FacturaForm()
    form.cliente_id.choices = clientes_choices
    for item in form.items:
        item.producto_id.choices = productos_choices
    if form.validate_on_submit():
        fecha_factura = datetime.combine(form.fecha.data, datetime.now().time()) if form.fecha.data else datetime.now()
        factura = Factura(id_cliente=form.cliente_id.data, fecha=fecha_factura)
        hubo_error = False
        for idx, item in enumerate(form.items):
            current_app.logger.info(
                f"Procesando item {idx}: producto_id={item.producto_id.data}, cantidad={item.cantidad.data}, precio={item.precio_unitario.data}"
            )
            producto = Producto.query.get(item.producto_id.data)
            if not producto:
                item.producto_id.errors.append('Producto inválido o inexistente')
                hubo_error = True
                continue
            try:
                cantidad_solicitada = int(item.cantidad.data or 0)
            except Exception:
                cantidad_solicitada = 0
            if cantidad_solicitada <= 0:
                item.cantidad.errors.append('Cantidad debe ser mayor a 0')
                hubo_error = True
                continue
            if (producto.stock or 0) < cantidad_solicitada:
                item.cantidad.errors.append('Cantidad supera el stock disponible')
                hubo_error = True
                continue
            detalle = DetalleFactura(
                id_producto=producto.id,
                cantidad=item.cantidad.data,
                precio_unitario=float(item.precio_unitario.data or 0),
                subtotal=float(item.cantidad.data or 0) * float(item.precio_unitario.data or 0)
            )
            factura.detalles.append(detalle)
        if hubo_error or len(factura.detalles) == 0:
            flash('Corrige los errores en los ítems de la factura.', 'danger')
            precios_por_producto = {p.id: p.precio for p in productos}
            return render_template("facturas/nueva_factura.html", form=form, productos=productos, precios_por_producto=precios_por_producto)
        
        try:
            factura.calcular_total()
            factura.actualizar_stock()
            db.session.add(factura)
            for detalle in factura.detalles:
                producto = detalle.producto or Producto.query.get(detalle.id_producto)
                if producto and producto.stock < 0:
                    raise ValueError(f"Stock insuficiente para el producto: {producto.descripcion}")
            db.session.commit()
            flash('Factura creada exitosamente', 'success')
            return redirect(url_for('main.listar_facturas'))
            
        except ValueError as ve:
            db.session.rollback()
            flash(str(ve), 'danger')
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception("Error al guardar la factura")
            flash(f"Error al guardar la factura: {str(e)}", 'danger')
        
        precios_por_producto = {p.id: p.precio for p in productos}
        return render_template("facturas/nueva_factura.html", form=form, productos=productos, precios_por_producto=precios_por_producto)
    elif request.method == 'POST':
        flash(f"Errores al validar la factura: {form.errors}", 'danger')
    precios_por_producto = {p.id: p.precio for p in productos}
    return render_template("facturas/nueva_factura.html", form=form, productos=productos, precios_por_producto=precios_por_producto)

@main_bp.route("/facturas/<int:id>")
@login_required
def ver_factura(id):
    factura = Factura.query.get_or_404(id)
    if getattr(current_user, "is_admin", False) or (factura.id_cliente == getattr(current_user, "id", None)):
        return render_template("facturas/ver_factura.html", factura=factura)
    return abort(403)

@main_bp.route("/reportes", methods=['GET', 'POST'])
@login_required
@admin_required
def reportes():
    try:
        current_app.logger.info("Accediendo a la ruta de reportes")
        form = ReporteForm()
        try:
            clientes = Cliente.query.all()
            form.cliente_id.choices = [(0, 'Todos')] + [(c.id, c.nombre) for c in clientes]
            current_app.logger.debug(f"Clientes cargados: {len(clientes)}")
        except Exception as e:
            current_app.logger.error(f"Error al cargar clientes: {str(e)}", exc_info=True)
            flash("Error al cargar la lista de clientes", 'danger')
            clientes = []
            form.cliente_id.choices = [(0, 'Todos')]
        
        resultados = {'facturas': [], 'ventas_total': 0, 'por_cliente': []}
        
        if form.validate_on_submit():
            try:
                current_app.logger.info(f"Generando reporte con datos: {form.data}")
                if form.fecha_desde.data > form.fecha_hasta.data:
                    flash("La fecha de inicio no puede ser posterior a la fecha final", 'danger')
                    return render_template('reportes.html', form=form, resultados=resultados)
                fecha_desde = form.fecha_desde.data
                fecha_hasta = form.fecha_hasta.data
                current_app.logger.debug(f"Buscando facturas entre {fecha_desde} y {fecha_hasta} (por fecha de día)")
                query = Factura.query.options(db.joinedload(Factura.cliente)).filter(
                    db.func.date(Factura.fecha) >= fecha_desde,
                    db.func.date(Factura.fecha) <= fecha_hasta,
                )

                if form.cliente_id.data != 0:
                    current_app.logger.debug(f"Filtrando por cliente ID: {form.cliente_id.data}")
                    query = query.filter(Factura.id_cliente == form.cliente_id.data)
                resultados['facturas'] = query.order_by(Factura.fecha.asc()).all()
                current_app.logger.debug(f"Se encontraron {len(resultados['facturas'])} facturas")
                resultados['ventas_total'] = sum(float(f.total) if f.total is not None else 0.0 for f in resultados['facturas'])
                totales = {}
                for factura in resultados['facturas']:
                    try:
                        cid = factura.id_cliente
                        cliente_nombre = factura.cliente.nombre if (factura and factura.cliente) else 'Cliente no encontrado'

                        if cid not in totales:
                            totales[cid] = {
                                'cliente_id': cid,
                                'cliente_nombre': cliente_nombre,
                                'monto_total': 0.0,
                                'cantidad': 0,
                            }

                        totales[cid]['monto_total'] += float(factura.total) if factura.total is not None else 0.0
                        totales[cid]['cantidad'] += 1

                    except Exception as e:
                        current_app.logger.error(f"Error procesando factura ID {getattr(factura, 'id', 'N/A')}: {str(e)}", exc_info=True)
                        continue

                resultados['por_cliente'] = sorted(totales.values(), key=lambda x: x['cliente_nombre'])
                current_app.logger.info("Reporte generado exitosamente")

            except Exception as e:
                current_app.logger.error(f"Error al generar reporte: {str(e)}", exc_info=True)
                flash(f"Error al generar el reporte: {str(e)}", 'danger')
                
        elif request.method == 'POST':
            error_msgs = ", ".join([f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()])
            current_app.logger.warning(f"Error de validación en el formulario: {error_msgs}")
            flash(f"Por favor corrija los errores en el formulario: {error_msgs}", 'danger')
            
        return render_template('reportes.html', form=form, resultados=resultados)
        
    except Exception as e:
        current_app.logger.critical(f"Error inesperado en reportes: {str(e)}", exc_info=True)
        flash("Ocurrió un error inesperado al procesar la solicitud. Por favor intente nuevamente.", 'danger')
        return render_template('reportes.html', form=form, resultados={'facturas': [], 'ventas_total': 0, 'por_cliente': []})

@main_bp.route("/facturas/eliminar/<int:id>", methods=['GET'])
@login_required
def confirmar_eliminar_factura(id):
    factura = Factura.query.get_or_404(id)
    return render_template("facturas/eliminar.html", factura=factura)

@main_bp.route("/facturas/eliminar/<int:id>", methods=['POST'])
@login_required
def eliminar_factura(id):
    factura = Factura.query.get_or_404(id)
    try:
        db.session.delete(factura)
        db.session.commit()
        flash('Factura eliminada correctamente', 'success')
        return redirect(url_for('main.listar_facturas'))
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error al eliminar factura {id}: {str(e)}')
        flash('Error al eliminar la factura', 'danger')
        return redirect(url_for('main.listar_facturas'))