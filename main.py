import flet as ft
import flet_charts as fch  # paquete separado: pip install flet-charts
import sqlite3
import datetime
import json
import random
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "serene_diary.db")

# ==========================================
# 1. CONFIGURACIÓN DE BASE DE DATOS LOCAL
# ==========================================

def init_db():
    """Inicializa la base de datos y crea la tabla si no existe."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            fecha TEXT PRIMARY KEY,
            mood TEXT,
            emotions TEXT,
            energy INTEGER,
            sleep_hours REAL,
            sleep_quality INTEGER,
            anxiety INTEGER,
            irritability INTEGER,
            medication TEXT,
            med_notes TEXT,
            exercise TEXT,
            consumption TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_checkin(data):
    """Guarda o actualiza un registro diario."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO checkins (
            fecha, mood, emotions, energy, sleep_hours, sleep_quality,
            anxiety, irritability, medication, med_notes, exercise, consumption, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['fecha'], data['mood'], json.dumps(data['emotions']), data['energy'],
        data['sleep_hours'], data['sleep_quality'], data['anxiety'], data['irritability'],
        data['medication'], data['med_notes'], data['exercise'], data['consumption'], data['notes']
    ))
    conn.commit()
    conn.close()


def get_recent_data(days=15):
    """Obtiene registros de los últimos N días ordenados por fecha."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fecha, mood, emotions, energy, sleep_hours, sleep_quality,
               anxiety, irritability, medication, med_notes, exercise, consumption, notes
        FROM checkins
        ORDER BY fecha ASC
    """)
    rows = cursor.fetchall()
    conn.close()

    data = []
    for r in rows:
        data.append({
            'fecha': r[0],
            'mood': r[1],
            'emotions': json.loads(r[2]) if r[2] else [],
            'energy': r[3] if r[3] is not None else 0,
            'sleep_hours': r[4] if r[4] is not None else 0.0,
            'sleep_quality': r[5] if r[5] is not None else 0,
            'anxiety': r[6] if r[6] is not None else 0,
            'irritability': r[7] if r[7] is not None else 0,
            'medication': r[8] if r[8] else "No",
            'med_notes': r[9] if r[9] else "",
            'exercise': r[10] if r[10] else "No",
            'consumption': r[11] if r[11] else "Ninguno",
            'notes': r[12] if r[12] else ""
        })
    return data[-days:]


def seed_mock_data():
    """Genera datos de simulación si la base de datos está completamente vacía."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM checkins")
    if cursor.fetchone()[0] == 0:
        hoy = datetime.date.today()
        for i in range(15, 0, -1):
            fecha = (hoy - datetime.timedelta(days=i)).isoformat()

            # Tendencia simulada para activar los algoritmos de 4 días
            if i <= 4:
                sleep_hours = 8.5 - (5 - i) * 0.8
                anxiety = 2 + (5 - i) * 1.5
                energy = max(10 - (5 - i) * 1.5, 2)
                mood = "Mal" if i == 1 else "Más o menos"
            else:
                sleep_hours = random.uniform(7.0, 9.0)
                anxiety = random.randint(1, 4)
                energy = random.randint(6, 9)
                mood = random.choice(["Increíble", "Bien", "Más o menos"])

            emotions = random.sample(["feliz", "calma", "amor", "ansiedad", "estres"], k=random.randint(1, 3))

            cursor.execute("""
                INSERT INTO checkins (
                    fecha, mood, emotions, energy, sleep_hours, sleep_quality,
                    anxiety, irritability, medication, med_notes, exercise, consumption, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fecha, mood, json.dumps(emotions), int(energy), float(sleep_hours),
                random.randint(6, 9), int(anxiety), random.randint(1, 4),
                "Sí", "Multivitamínicos", "Sí", "Ninguno", "Día simulado para pruebas de la app."
            ))
        conn.commit()
    conn.close()


# ==========================================
# 2. COLORES PASTEL
# ==========================================
COLOR_GREY_BG = "#F3F4F6"
COLOR_CREAM = "#FCF6BD"
COLOR_PEACH = "#FDE4CF"
COLOR_PINK = "#FFCAD4"
COLOR_LAVENDER_PINK = "#F4B3F4"
COLOR_LAVENDER = "#CFBAF0"
COLOR_PERIWINKLE = "#A3C4F3"
COLOR_CYAN = "#8EECF5"
COLOR_MINT = "#B9FBC0"
COLOR_WHITE = "#FFFFFF"
COLOR_DARK_TEXT = "#1F2937"

MOOD_COLORS = {
    "Increíble": COLOR_MINT,
    "Bien": COLOR_CYAN,
    "Más o menos": COLOR_PEACH,
    "Mal": COLOR_PINK,
    "Horrible": COLOR_LAVENDER_PINK
}


# ==========================================
# 3. INTERFAZ DE USUARIO EN FLET
# ==========================================
def main(page: ft.Page):
    page.title = "Serene - Diario Inteligente de Bienestar"
    page.bgcolor = COLOR_GREY_BG
    page.padding = 20

    page.window.width = 410
    page.window.height = 840
    page.scroll = ft.ScrollMode.AUTO

    init_db()
    seed_mock_data()

    # Estado del formulario diario
    state = {"mood": "Bien"}
    selected_emotions = set()

    # Componentes del formulario
    energy_slider = ft.Slider(min=1, max=10, value=7, divisions=9, label="{value}", active_color=COLOR_PERIWINKLE)

    sleep_hours_input = ft.TextField(
        label="Horas", value="8.0", keyboard_type=ft.KeyboardType.NUMBER,
        width=80, border_color=COLOR_LAVENDER
    )
    sleep_quality_slider = ft.Slider(min=1, max=10, value=7, divisions=9, label="{value}", active_color=COLOR_CYAN)
    anxiety_slider = ft.Slider(min=1, max=10, value=3, divisions=9, label="{value}", active_color=COLOR_PINK)
    irritability_slider = ft.Slider(min=1, max=10, value=2, divisions=9, label="{value}", active_color=COLOR_PEACH)
    med_taken = ft.Switch(label="Medicación tomada", value=False, active_color=COLOR_MINT)
    med_notes_input = ft.TextField(label="Notas de medicación / dosis", hint_text="Ej. Sertralina 50mg", border_color=COLOR_LAVENDER)
    exercise_switch = ft.Switch(label="Actividad Física", value=True, active_color=COLOR_MINT)

    alcohol_check = ft.Checkbox(label="Alcohol", value=False, fill_color=COLOR_PEACH)
    tabaco_check = ft.Checkbox(label="Tabaco", value=False, fill_color=COLOR_PEACH)
    otro_check = ft.Checkbox(label="Otro", value=False, fill_color=COLOR_PEACH)

    notes_input = ft.TextField(label="Espacio de notas / Desahogo", multiline=True, min_lines=3, border_color=COLOR_LAVENDER)

    alerts_container = ft.Column(spacing=10)

    # ==========================================
    # LÓGICA DE DETECCIÓN DE PATRONES
    # ==========================================
    def check_for_patterns():
        """Analiza tendencias usando umbrales tolerantes para datos reales."""
        alerts_container.controls.clear()
        data = get_recent_data(days=4)
        if len(data) < 4:
            alerts_container.controls.append(
                ft.Text("Necesitas al menos 4 días de registros para detectar patrones.", size=13, color="grey")
            )
            page.update()
            return

        sleeps = [d['sleep_hours'] for d in data]
        anxieties = [d['anxiety'] for d in data]

        # Antes solo comparaba 3 de los 4 días (range(2)); ahora compara los 4 (range(3))
        if sleeps[0] > sleeps[3] and all(sleeps[i] >= sleeps[i + 1] for i in range(3)):
            alerts_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.BEDTIME_OUTLINED, color="#5B21B6"),
                            ft.Text("Patrón Detectado: Sueño en declive", weight=ft.FontWeight.BOLD, color="#5B21B6")
                        ]),
                        ft.Text(
                            f"Tu tiempo de sueño ha disminuido consecutivamente de {sleeps[0]:.1f}h a {sleeps[3]:.1f}h en los últimos días. Te recomendamos descansar.",
                            size=13, color="#4C1D95"
                        )
                    ]),
                    bgcolor=COLOR_LAVENDER,
                    padding=15,
                    border_radius=15,
                )
            )

        if anxieties[3] > anxieties[0] and all(anxieties[i] <= anxieties[i + 1] for i in range(3)):
            alerts_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color="#991B1B"),
                            ft.Text("Alerta: Ansiedad en aumento", weight=ft.FontWeight.BOLD, color="#991B1B")
                        ]),
                        ft.Text(
                            "Hemos notado un incremento paulatino en tus niveles de ansiedad en los últimos 4 días. Considera hacer una pausa activa.",
                            size=13, color="#7F1D1D"
                        )
                    ]),
                    bgcolor=COLOR_PINK,
                    padding=15,
                    border_radius=15,
                )
            )

        if len(alerts_container.controls) == 0:
            alerts_container.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color="#065F46"),
                        ft.Text("No se detectan patrones de riesgo de 4 días. ¡Vas excelente!", color="#065F46", size=13)
                    ]),
                    bgcolor=COLOR_MINT,
                    padding=12,
                    border_radius=12
                )
            )
        page.update()

    # ==========================================
    # GRÁFICOS E HISTORIAL
    # ==========================================
    charts_container = ft.Column(spacing=20)

    def draw_charts():
        charts_container.controls.clear()
        data = get_recent_data(days=7)

        if len(data) < 2:
            charts_container.controls.append(
                ft.Text("Aún no hay suficientes datos para graficar.", color=COLOR_DARK_TEXT)
            )
            page.update()
            return

        points_energy = []
        points_anxiety = []
        bottom_labels = []
        for index, day in enumerate(data):
            # flet_charts.LineChartData usa la propiedad `points`, no `data_points`
            points_energy.append(fch.LineChartDataPoint(index, day['energy']))
            points_anxiety.append(fch.LineChartDataPoint(index, day['anxiety']))
            bottom_labels.append(
                fch.ChartAxisLabel(
                    value=index,
                    label=ft.Text(day['fecha'][5:], size=9)  # MM-DD
                )
            )

        energy_series = fch.LineChartData(
            points=points_energy,
            stroke_width=4,
            color=COLOR_PERIWINKLE,
            curved=True,
            rounded_stroke_cap=True,  # nombre correcto (no "stroke_cap_round")
        )

        anxiety_series = fch.LineChartData(
            points=points_anxiety,
            stroke_width=4,
            color=COLOR_PINK,
            curved=True,
            rounded_stroke_cap=True,
        )

        line_chart = fch.LineChart(
            data_series=[energy_series, anxiety_series],
            border=ft.Border.only(bottom=ft.BorderSide(1, "grey")),
            left_axis=fch.ChartAxis(label_size=40),
            bottom_axis=fch.ChartAxis(label_size=30, labels=bottom_labels),
            horizontal_grid_lines=fch.ChartGridLines(interval=2, color="#E5E7EB", width=1),
            min_y=0,
            max_y=10,
            min_x=0,
            max_x=len(data) - 1,
            expand=True,
            height=200,
        )

        charts_container.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("Relación Energía (Azul) vs Ansiedad (Rosa)", weight=ft.FontWeight.BOLD, size=14, color=COLOR_DARK_TEXT),
                    line_chart,
                    ft.Text("Últimos 7 días analizados", size=11, color="grey")
                ]),
                bgcolor=COLOR_WHITE,
                padding=15,
                border_radius=18,
                shadow=ft.BoxShadow(blur_radius=10, color="#0D000000")
            )
        )

        notes_list = ft.Column(spacing=10)
        has_notes = False
        for day in reversed(data):
            if day['notes'].strip():
                has_notes = True
                notes_list.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(day['fecha'], size=11, weight=ft.FontWeight.BOLD),
                                ft.Container(
                                    content=ft.Text(day['mood'], size=10, color=COLOR_DARK_TEXT),
                                    bgcolor=MOOD_COLORS.get(day['mood'], COLOR_PEACH),
                                    padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=10
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(day['notes'], size=13, italic=True)
                        ]),
                        bgcolor=COLOR_WHITE,
                        padding=12,
                        border_radius=12
                    )
                )

        if not has_notes:
            notes_list.controls.append(
                ft.Text("Aún no has escrito notas en tus últimos registros.", size=12, color="grey")
            )

        charts_container.controls.append(
            ft.Column([
                ft.Text("Tu Bitácora Reciente", weight=ft.FontWeight.BOLD, size=15, color=COLOR_DARK_TEXT),
                notes_list
            ])
        )
        page.update()

    # ==========================================
    # MANEJADORES DE ACCIONES
    # ==========================================
    def handle_mood_click(e, mood_name):
        state["mood"] = mood_name
        for container in mood_row.controls:
            container.border = ft.Border.all(3, COLOR_DARK_TEXT) if container.data == mood_name else None
        page.update()

    def handle_emotion_toggle(e, emotion_name):
        if emotion_name in selected_emotions:
            selected_emotions.remove(emotion_name)
            e.control.bgcolor = COLOR_WHITE
            e.control.content.color = COLOR_DARK_TEXT
        else:
            selected_emotions.add(emotion_name)
            e.control.bgcolor = COLOR_LAVENDER
            e.control.content.color = COLOR_WHITE
        page.update()

    def reset_emotion_chips():
        """Limpia visualmente y lógicamente la selección de emociones tras guardar."""
        selected_emotions.clear()
        for chip in emotions_wrap.controls:
            chip.bgcolor = COLOR_WHITE
            chip.content.color = COLOR_DARK_TEXT

    def on_save_click(e):
        try:
            val_sleep = float(sleep_hours_input.value) if sleep_hours_input.value else 8.0
        except ValueError:
            val_sleep = 8.0
            sleep_hours_input.value = "8.0"

        cons_list = []
        if alcohol_check.value:
            cons_list.append("Alcohol")
        if tabaco_check.value:
            cons_list.append("Tabaco")
        if otro_check.value:
            cons_list.append("Otro")

        data_to_save = {
            'fecha': datetime.date.today().isoformat(),
            'mood': state['mood'],
            'emotions': list(selected_emotions),
            'energy': int(energy_slider.value),
            'sleep_hours': val_sleep,
            'sleep_quality': int(sleep_quality_slider.value),
            'anxiety': int(anxiety_slider.value),
            'irritability': int(irritability_slider.value),
            'medication': "Sí" if med_taken.value else "No",
            'med_notes': med_notes_input.value if med_notes_input.value else "",
            'exercise': "Sí" if exercise_switch.value else "No",
            'consumption': ", ".join(cons_list) if cons_list else "Ninguno",
            'notes': notes_input.value if notes_input.value else ""
        }

        save_checkin(data_to_save)

        # page.open() no existe en esta versión de Flet: se usa page.show_dialog()
        sb = ft.SnackBar(ft.Text("¡Tu día se ha guardado con éxito!"), bgcolor=COLOR_MINT)
        page.show_dialog(sb)

        check_for_patterns()
        draw_charts()
        page.update()

    # ==========================================
    # CREACIÓN DE VISTAS (PANTALLAS)
    # ==========================================
    moods_definition = [
        ("🤩", "Increíble"),
        ("🙂", "Bien"),
        ("😐", "Más o menos"),
        ("🙁", "Mal"),
        ("😭", "Horrible")
    ]

    mood_row = ft.Row(spacing=8, scroll=ft.ScrollMode.AUTO)
    for emoji, name in moods_definition:
        is_selected = name == state["mood"]
        container_mood = ft.Container(
            data=name,  # antes usaba `key`, que es para reconciliación interna, no datos
            content=ft.Column([
                ft.Text(emoji, size=24),
                ft.Text(name, size=10, weight=ft.FontWeight.W_500)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=MOOD_COLORS[name],
            padding=10,
            border_radius=15,
            alignment=ft.Alignment.CENTER,
            on_click=lambda e, n=name: handle_mood_click(e, n),
            border=ft.Border.all(3, COLOR_DARK_TEXT) if is_selected else None,
            width=70
        )
        mood_row.controls.append(container_mood)

    emotions_list = ["Feliz", "Triste", "Miedo", "Enojo", "Amor", "Vergüenza", "Ansiedad", "Calma", "Estrés"]
    emotions_wrap = ft.Row(wrap=True, spacing=8, run_spacing=8)
    for emo in emotions_list:
        emotions_wrap.controls.append(
            ft.Container(
                content=ft.Text(emo, color=COLOR_DARK_TEXT, size=12),
                bgcolor=COLOR_WHITE,
                border=ft.Border.all(1, "#E5E7EB"),
                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                border_radius=20,
                on_click=lambda e, name=emo.lower(): handle_emotion_toggle(e, name)
            )
        )

    tab_checkin = ft.Column([
        ft.Text("Registro de Hoy", size=22, weight=ft.FontWeight.BOLD, color=COLOR_DARK_TEXT),
        ft.Text("¿Cómo te sientes en general hoy?", size=14, color="grey"),
        mood_row,

        ft.Divider(height=10, color="transparent"),
        ft.Text("Emociones detectadas", size=14, weight=ft.FontWeight.BOLD, color=COLOR_DARK_TEXT),
        emotions_wrap,

        ft.Divider(height=10, color="transparent"),
        ft.Row([
            ft.Icon(ft.Icons.BOLT, color=COLOR_PEACH),
            ft.Text("Nivel de Energía", size=14, weight=ft.FontWeight.BOLD, color=COLOR_DARK_TEXT)
        ]),
        energy_slider,

        ft.Row([
            ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.BED, color=COLOR_LAVENDER),
                    ft.Text("Sueño", size=14, weight=ft.FontWeight.BOLD, color=COLOR_DARK_TEXT)
                ]),
                sleep_hours_input,
            ], expand=1),
            ft.Column([
                ft.Text("Calidad de Sueño", size=14, weight=ft.FontWeight.BOLD, color=COLOR_DARK_TEXT),
                sleep_quality_slider,
            ], expand=2)
        ]),

        ft.Divider(height=10, color="transparent"),
        ft.Row([
            ft.Icon(ft.Icons.CORONAVIRUS_ROUNDED, color=COLOR_PINK),
            ft.Text("Ansiedad (1-10)", size=14, weight=ft.FontWeight.BOLD, color=COLOR_DARK_TEXT)
        ]),
        anxiety_slider,

        ft.Row([
            ft.Icon(ft.Icons.MOOD_BAD_ROUNDED, color=COLOR_PEACH),
            ft.Text("Irritabilidad (1-10)", size=14, weight=ft.FontWeight.BOLD, color=COLOR_DARK_TEXT)
        ]),
        irritability_slider,

        ft.Divider(height=10, color="transparent"),
        ft.Text("Estilo de Vida y Hábitos", size=15, weight=ft.FontWeight.BOLD, color=COLOR_DARK_TEXT),
        ft.Container(
            content=ft.Column([
                med_taken,
                med_notes_input,
                exercise_switch,
                ft.Text("Consumos hoy:", size=13, weight=ft.FontWeight.BOLD),
                ft.Row([alcohol_check, tabaco_check, otro_check], spacing=10),
            ]),
            bgcolor=COLOR_WHITE,
            padding=15,
            border_radius=15,
        ),

        ft.Divider(height=10, color="transparent"),
        notes_input,

        ft.Button(
            content="Guardar mi día",
            on_click=on_save_click,
            bgcolor=COLOR_MINT,
            color=COLOR_DARK_TEXT,
            width=350,
            height=45,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=15))
        )
    ], spacing=15, scroll=ft.ScrollMode.AUTO)

    tab_trends = ft.Column([
        ft.Text("Tendencias & Análisis", size=22, weight=ft.FontWeight.BOLD, color=COLOR_DARK_TEXT),
        ft.Text("Sugerencias Activas", size=15, weight=ft.FontWeight.BOLD, color=COLOR_DARK_TEXT),
        alerts_container,
        ft.Divider(height=10, color="transparent"),
        charts_container
    ], spacing=15, scroll=ft.ScrollMode.AUTO)

    content_area = ft.Container(content=tab_checkin, expand=True)

    def on_tab_change(e):
        if e.control.selected_index == 0:
            content_area.content = tab_checkin
        elif e.control.selected_index == 1:
            content_area.content = tab_trends
            check_for_patterns()
            draw_charts()
        page.update()

    # NavigationDestination -> nombre correcto es NavigationBarDestination
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.EDIT_NOTE, label="Diario"),
            ft.NavigationBarDestination(icon=ft.Icons.SHOW_CHART, label="Tendencias"),
        ],
        selected_index=0,
        on_change=on_tab_change,
        bgcolor=COLOR_WHITE,
    )

    page.add(content_area)


if __name__ == "__main__":
    ft.run(main)
