import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Gio

class LaunchpadWindow(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        
        # Forzar color de texto blanco para las etiquetas mediante CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"label { color: white; }")
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        # Configurar ventana a pantalla completa y sin bordes
        self.set_decorated(False)
        self.fullscreen()
        
        # Fondo semitransparente estilo macOS blur
        self.set_app_paintable(True)
        self.connect("draw", self.on_draw)
        
        # Contenedor principal
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        main_box.set_margin_top(50)
        main_box.set_margin_bottom(50)
        main_box.set_margin_start(50)
        main_box.set_margin_end(50)
        self.add(main_box)
        
        # Barra de búsqueda superior
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Buscar aplicaciones...")
        self.search_entry.set_halign(Gtk.Align.CENTER)
        self.search_entry.set_width_chars(30)
        self.search_entry.connect("search-changed", self.on_search_changed)
        main_box.pack_start(self.search_entry, False, False, 0)
        
        # Área de desplazamiento para la cuadrícula de iconos
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        main_box.pack_start(scrolled, True, True, 0)
        
        # Cuadrícula (FlowBox) para los iconos
        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(6)
        self.flowbox.set_min_children_per_line(4)
        self.flowbox.set_row_spacing(20)
        self.flowbox.set_column_spacing(20)
        self.flowbox.set_halign(Gtk.Align.CENTER)
        
        # Configurar la función de filtro para el FlowBox
        self.flowbox.set_filter_func(self.filter_apps_func)
        
        scrolled.add(self.flowbox)
        
        # Cargar aplicaciones del sistema
        self.load_applications()
        
        # Evento para cerrar con la tecla Escape
        self.connect("key-press-event", self.on_key_press)
        
        self.show_all()

    def on_draw(self, widget, cr):
        # Fondo oscuro translúcido
        cr.set_source_rgba(0.1, 0.1, 0.1, 0.85)
        cr.paint()
        return False

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.destroy()

    def load_applications(self):
        # Obtener aplicaciones instaladas
        app_infos = Gio.AppInfo.get_all()
        for app_info in app_infos:
            if app_info.should_show():
                name = app_info.get_name()
                icon = app_info.get_icon()
                
                # Crear botón para cada app
                button = Gtk.Button()
                button.set_relief(Gtk.ReliefStyle.NONE)
                
                # Guardar el nombre en el botón para facilitar el filtrado
                button.app_name = name.lower()
                
                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
                box.set_halign(Gtk.Align.CENTER)
                
                # Cargar icono
                image = Gtk.Image()
                if icon:
                    icon_theme = Gtk.IconTheme.get_default()
                    icon_info = icon_theme.lookup_by_gicon(icon, 64, Gtk.IconLookupFlags.FORCE_SYMBOLIC)
                    image.set_from_gicon(icon, Gtk.IconSize.DIALOG)
                else:
                    image.set_from_icon_name("application-default-icon", Gtk.IconSize.DIALOG)
                
                label = Gtk.Label(label=name)
                label.set_max_width_chars(15)
                label.set_ellipsize(3) # Puntos suspensivos si es muy largo
                
                box.pack_start(image, False, False, 0)
                box.pack_start(label, False, False, 0)
                button.add(box)
                
                # Lanzar la aplicación al hacer clic
                app_copy = app_info
                button.connect("clicked", lambda b, a=app_copy: self.launch_app(a))
                
                self.flowbox.add(button)

    def on_search_changed(self, entry):
        # Actualiza el filtro del FlowBox cada vez que se escribe en la barra
        self.flowbox.invalidate_filter()

    def filter_apps_func(self, child):
        # Obtiene el texto de búsqueda en minúsculas
        search_text = self.search_entry.get_text().lower()
        if not search_text:
            return True
        
        # Compara si el nombre de la app contiene el texto buscado
        return search_text in child.get_child().app_name

    def launch_app(self, app_info):
        app_info.launch([], None)
        self.destroy()

if __name__ == "__main__":
    win = LaunchpadWindow()
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()
