# -*- coding: utf-8 -*-
"""
Книга-игра: Тайна особняка Корвус
"""
import os
os.environ['KIVY_NO_CONSOLELOGFILE'] = '1'

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.storage.jsonstore import JsonStore
import datetime

Config.set('graphics', 'width', '420')
Config.set('graphics', 'height', '720')
Config.set('graphics', 'resizable', '0')
Config.set('kivy', 'exit_on_escape', '1')

Window.clearcolor = (0.05, 0.05, 0.08, 1)

from story_data import STORY


class GameData:
    def __init__(self):
        self.store = JsonStore('save_game.json')
        self.reset()
    
    def reset(self):
        self.current_chapter = "chapter_1"
        self.visited_chapters = ["chapter_1"]
        self.journal = []
        self.choices_history = []
        
    def load(self):
        if self.store.exists('save'):
            data = self.store.get('save')
            self.current_chapter = data['current_chapter']
            self.visited_chapters = data['visited_chapters']
            self.journal = data['journal']
            self.choices_history = data['choices_history']
            return True
        return False
    
    def save(self):
        data = {
            'current_chapter': self.current_chapter,
            'visited_chapters': self.visited_chapters,
            'journal': self.journal,
            'choices_history': self.choices_history,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self.store.put('save', **data)
    
    def add_to_journal(self, text):
        chapter = STORY[self.current_chapter]
        title = chapter.get('title', 'Глава')
        entry = f"{title}: {text[:60]}..."
        if entry not in self.journal:
            self.journal.append(entry)
            if len(self.journal) > 25:
                self.journal.pop(0)
    
    def add_choice(self, choice_text):
        self.choices_history.append(choice_text)
    
    def go_to_chapter(self, chapter_id):
        if chapter_id in STORY:
            self.current_chapter = chapter_id
            if chapter_id not in self.visited_chapters:
                self.visited_chapters.append(chapter_id)
    
    def get_stats_text(self):
        return f"Глав пройдено: {len(self.visited_chapters)}"
    
    def get_journal_text(self):
        return "\n\n".join(reversed(self.journal)) if self.journal else "Записей пока нет"


class GameApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_data = GameData()
        self.main_screen = None
        self.title_label = None
        self.story_label = None
        self.story_scroll = None
        self.choices_box = None
        self.journal_content = None
        self.stats_content = None
        self.save_msg = None
    
    def build(self):
        sm = ScreenManager()
        
        main = Screen(name='main')
        main_layout = BoxLayout(orientation='vertical', padding=6, spacing=4)
        
        self.title_label = Label(text="", font_size='21sp', color=[1, 0.85, 0.2, 1], halign='center', size_hint_y=None, height='48dp', bold=True)
        
        menu_bar = GridLayout(cols=3, size_hint_y=None, height='42dp', spacing=6)
        for txt, scr in [('ЖУРНАЛ', 'journal'), ('СТАТИСТ', 'stats'), ('СОХРАН', 'saveload')]:
            btn = Button(text=txt, font_size='13sp', background_color=[0.12, 0.12, 0.18, 1], color=[0.85, 0.8, 0.6, 1], bold=True)
            btn.bind(on_press=lambda x, s=scr: setattr(sm, 'current', s))
            menu_bar.add_widget(btn)
        
        self.story_scroll = ScrollView(do_scroll_x=False, do_scroll_y=True, size_hint_y=1, scroll_y=0, bar_width=6, scroll_type=['bars'])
        story_container = BoxLayout(orientation='vertical', size_hint_y=None, padding=8, spacing=4)
        story_container.bind(minimum_height=story_container.setter('height'))
        self.story_label = Label(text="", font_size='15sp', color=[0.88, 0.88, 0.82, 1], line_height=1.4, text_size=(390, None), markup=False, size_hint_y=None)
        story_container.add_widget(self.story_label)
        self.story_scroll.add_widget(story_container)
        
        self.choices_box = BoxLayout(orientation='vertical', spacing=8, size_hint_y=None, padding=(8, 4))
        self.choices_box.bind(minimum_height=self.choices_box.setter('height'))
        
        main_layout.add_widget(self.title_label)
        main_layout.add_widget(menu_bar)
        main_layout.add_widget(self.story_scroll)
        main_layout.add_widget(self.choices_box)
        main.add_widget(main_layout)
        sm.add_widget(main)
        self.main_screen = main
        
        journal = Screen(name='journal')
        jour_layout = BoxLayout(orientation='vertical', padding=12, spacing=8)
        jour_layout.add_widget(Label(text='📖 ЖУРНАЛ', font_size='20sp', color=[0.95, 0.75, 0.15, 1], size_hint_y=None, height='40dp'))
        jour_layout.add_widget(Button(text='← НАЗАД', size_hint_y=None, height='40dp', background_color=[0.15, 0.15, 0.2, 1], color=[0.8, 0.8, 0.8, 1], on_press=lambda x: setattr(sm, 'current', 'main')))
        jscroll = ScrollView(do_scroll_x=False)
        self.journal_content = Label(text='', font_size='14sp', color=[0.8, 0.8, 0.75, 1], line_height=1.3)
        jscroll.add_widget(self.journal_content)
        jour_layout.add_widget(jscroll)
        journal.add_widget(jour_layout)
        sm.add_widget(journal)
        
        stats = Screen(name='stats')
        stat_layout = BoxLayout(orientation='vertical', padding=12, spacing=8)
        stat_layout.add_widget(Label(text='📊 СТАТИСТИКА', font_size='20sp', color=[0.95, 0.75, 0.15, 1], size_hint_y=None, height='40dp'))
        stat_layout.add_widget(Button(text='← НАЗАД', size_hint_y=None, height='40dp', background_color=[0.15, 0.15, 0.2, 1], color=[0.8, 0.8, 0.8, 1], on_press=lambda x: setattr(sm, 'current', 'main')))
        self.stats_content = Label(text='', font_size='18sp', color=[0.8, 0.8, 0.75, 1])
        stat_layout.add_widget(self.stats_content)
        stats.add_widget(stat_layout)
        sm.add_widget(stats)
        
        saveload = Screen(name='saveload')
        save_layout = BoxLayout(orientation='vertical', padding=15, spacing=12)
        save_layout.add_widget(Label(text='💾 СОХРАНЕНИЕ', font_size='20sp', color=[0.95, 0.75, 0.15, 1], size_hint_y=None, height='40dp'))
        self.save_msg = Label(text='', font_size='14sp', color=[0.3, 0.9, 0.4, 1], size_hint_y=None, height='30dp')
        save_layout.add_widget(self.save_msg)
        
        save_btn = Button(text='💾 СОХРАНИТЬ', size_hint_y=None, height='50dp', background_color=[0.1, 0.5, 0.2, 1], color=[1, 1, 1, 1])
        save_btn.bind(on_press=self.save_game)
        save_layout.add_widget(save_btn)
        
        load_btn = Button(text='📂 ЗАГРУЗИТЬ', size_hint_y=None, height='50dp', background_color=[0.1, 0.3, 0.6, 1], color=[1, 1, 1, 1])
        load_btn.bind(on_press=self.load_game)
        save_layout.add_widget(load_btn)
        
        new_btn = Button(text='🔄 НОВАЯ ИГРА', size_hint_y=None, height='50dp', background_color=[0.6, 0.2, 0.2, 1], color=[1, 1, 1, 1])
        new_btn.bind(on_press=self.new_game)
        save_layout.add_widget(new_btn)
        
        save_layout.add_widget(Button(text='← НАЗАД', size_hint_y=None, height='40dp', background_color=[0.15, 0.15, 0.2, 1], color=[0.8, 0.8, 0.8, 1], on_press=lambda x: setattr(sm, 'current', 'main')))
        saveload.add_widget(save_layout)
        sm.add_widget(saveload)
        
        self.update_story()
        
        return sm
    
    def update_story(self, reset_scroll=True):
        gd = self.game_data
        ch = STORY[gd.current_chapter]
        
        self.title_label.text = ch.get('title', '')
        self.story_label.text = ch['text']
        
        if reset_scroll:
            Clock.schedule_once(self._reset_scroll, 0.1)
        
        if gd.current_chapter == "chapter_1":
            pass
        else:
            gd.add_to_journal(ch['text'])
        
        self.choices_box.clear_widgets()
        for choice in ch.get('choices', []):
            btn = Button(
                text=choice['text'],
                size_hint_y=None,
                height='56dp',
                background_color=[0.1, 0.12, 0.16, 1],
                color=[0.95, 0.9, 0.75, 1],
                font_size='14sp',
                border=(0, 0, 0, 0),
                background_normal='',
                padding=(10, 0)
            )
            btn.bind(on_press=lambda x, c=choice: self.make_choice(c))
            self.choices_box.add_widget(btn)
    
    def _reset_scroll(self, *args):
        self.story_scroll.scroll_y = 0
        self.story_scroll._scroll_y = 0
    
    def make_choice(self, choice):
        self.game_data.add_choice(choice['text'])
        self.game_data.go_to_chapter(choice.get('next', 'chapter_1'))
        self.update_story(reset_scroll=True)
        self.root.current = 'main'
    
    def save_game(self, instance):
        self.game_data.save()
        self.save_msg.text = "✅ Игра сохранена!"
    
    def load_game(self, instance):
        if self.game_data.load():
            self.save_msg.text = "✅ Игра загружена!"
            self.update_story()
            self.root.current = 'main'
        else:
            self.save_msg.text = "❌ Нет сохранения"
    
    def new_game(self, instance):
        self.game_data.reset()
        self.update_story(reset_scroll=True)
        self.save_msg.text = "✅ Новая игра!"
        self.root.current = 'main'
    
    def on_pause(self):
        self.game_data.save()
        return True
    
    def on_stop(self):
        self.game_data.save()


if __name__ == '__main__':
    GameApp().run()
