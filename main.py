import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from pygame.font import Font
from pygame.color import Color
import pyautogui
import time
import conf
import keyboard
import json
import datetime as dt
import traceback

pygame.init()
SCREEN_INFO = pygame.display.Info()
SCREEN_W, SCREEN_H = SCREEN_INFO.current_w, SCREEN_INFO.current_h
vh, vw = SCREEN_H / 100, SCREEN_W / 100


class Statictics:

    def __init__(self):
        self.filename = 'statistics.json'

        self.WORK = 'work'
        self.REST = 'rest'
        self.USER_REST = 'user_rest'

        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as file:
                json.dump({'actions': []}, file)

    def add_action(
            self,
            type: str,
            start_time: dt.datetime,
            finish_time: dt.datetime,
            task: str = None
    ):
        obj = {
            'type': type,
            'start_time': start_time.strftime('%d.%m.%Y %X'),
            'finish_time': finish_time.strftime('%d.%m.%Y %X'),
            'task': task
        }

        with open(self.filename, 'r') as file:
            data = json.load(file)
        
        data['actions'].append(obj)

        with open(self.filename, 'w') as file:
            json.dump(data, file)

    def end_work(self, duration):
        self.add_action(
            self.WORK,
            dt.datetime.now() - dt.timedelta(seconds=duration),
            dt.datetime.now()
        )

    def end_rest(self, duration):
        self.add_action(
            self.REST,
            dt.datetime.now() - dt.timedelta(seconds=duration),
            dt.datetime.now()
        )

    def end_user_rest(self, duration):
        self.add_action(
            self.USER_REST,
            dt.datetime.now() - dt.timedelta(seconds=duration),
            dt.datetime.now()
        )


def set_user_settings():
    if not os.path.exists('user_settings.json'):
        d = {}
    else:
        with open('user_settings.json', 'r') as file:
            d = json.load(file)

    if 'work_duration' not in d:
        print('Привет! Это программа для управление временем - она напомнит сделать перерыв, чтобы ты не терял фокус. Давай выберем подходящие настройки. Скоро эта настройка должна получить графический интерфейс :)')
        work_duration = None
        while work_duration is None:
            work_duration = input('Введи длительность периода работы в минутах (рекомендуемое значение - 25): ')
            if work_duration.isdigit():
                work_duration = int(work_duration)
            else:
                work_duration = None
        d['work_duration'] = work_duration * 60

    if 'rest_duration' not in d:
        rest_duration = None
        while rest_duration is None:
            rest_duration = input('Введи длительность перерыва в минутах (рекомендуемое значение - 5): ')
            if rest_duration.isdigit():
                rest_duration = int(rest_duration)
            else:
                rest_duration = None
        d['rest_duration'] = rest_duration * 60

    if 'title_font_size' not in d:
        d['title_font_size'] = int(round(9 * vh))

    if 'subtitle_font_size' not in d:
        d['subtitle_font_size'] = int(round(3 * vh))

    with open('user_settings.json', 'w') as file:
        json.dump(d, file)


def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ''

    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + ' '
    
    if current_line:  # добавляем последнюю строку
        lines.append(current_line)
    
    return lines


def time_to_str(s):
    s = int(round(s))
    m = str(s // 60).rjust(2, '0')
    s = str(s % 60).rjust(2, '0')
    return f'{m}:{s}'


def rest(duration):

    with open('user_settings.json', 'r') as file:
        r = json.load(file)
        title_font_size = r.get('title_font_size')
        subtitle_font_size = r.get('subtitle_font_size')

    start_time = time.time()

    pyautogui.screenshot().save(conf.screenshot_path)
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)

    image = pygame.image.load(conf.screenshot_path).convert_alpha()
    image = pygame.transform.scale(image, (SCREEN_W, SCREEN_H))

    image_alpha = 255
    text_alpha = 0

    f_t = Font(conf.title_font_path, title_font_size)
    f_st = Font(conf.subtitle_font_path, subtitle_font_size)

    title = 'Перерыв'

    running = True
    while running:
        
        if duration is not None and time.time() - start_time < duration:
            subtitle = time_to_str(duration - (time.time() - start_time))
        elif duration is not None and time.time() - start_time >= duration:
            title = 'Перерыв завершен'
            subtitle = '00:00 (нажми любую кнопку, чтобы начать работу)'
        else:
            subtitle = time_to_str(time.time() - start_time) + ' (esc для выхода)'
        
        if keyboard.is_pressed('esc'):
            if duration is None:
                statistics.end_user_rest(time.time() - start_time)
            else:
                statistics.end_rest(time.time() - start_time)

            running = False
            break

        image.set_alpha(image_alpha)

        wrapped_title = wrap_text(title, f_t, conf.max_width_title * vw)
        wrapped_subtitle = wrap_text(subtitle, f_st, conf.max_width_subtitle * vw)

        total_height_title = sum(f_t.size(line)[1] for line in wrapped_title)
        total_height_subtitle = sum(f_st.size(line)[1] for line in wrapped_subtitle)
        
        total_height = total_height_title + total_height_subtitle
        y_start = (SCREEN_H - total_height) // 2

        title_rects = []
        subtitle_rects = []

        for line in wrapped_title:
            title_surface = f_t.render(line, True, Color(*conf.title_color))
            title_rect = title_surface.get_rect(center=(50 * vw, y_start))
            title_rects.append((title_surface, title_rect))
            y_start += title_surface.get_height()

        for line in wrapped_subtitle:
            subtitle_surface = f_st.render(line, True, Color(*conf.subtitle_color))
            subtitle_rect = subtitle_surface.get_rect(center=(50 * vw, y_start))
            subtitle_rects.append((subtitle_surface, subtitle_rect))
            y_start += subtitle_surface.get_height()

        title_alpha = text_alpha
        subtitle_alpha = text_alpha

        title_surface, title_rect = title_rects[0] if title_rects else (None, None)
        subtitle_surface, subtitle_rect = subtitle_rects[0] if subtitle_rects else (None, None)

        for surface, rect in title_rects:
            surface.set_alpha(title_alpha)

        for surface, rect in subtitle_rects:
            surface.set_alpha(subtitle_alpha)

        screen.fill(Color(*conf.bg_color))
        if image_alpha > 0:
            image_alpha = max(image_alpha - 5, 0)
            screen.blit(image, (0, 0))
        else:
            text_alpha = min(text_alpha + 5, 255)
            for surface, rect in title_rects:
                screen.blit(surface, rect)

            for surface, rect in subtitle_rects:
                screen.blit(surface, rect)

        pygame.display.flip()

        if duration is not None and time.time() - start_time >= duration:
            keyboard.read_key()

            if duration is None:
                statistics.end_user_rest(time.time() - start_time)
            else:
                statistics.end_rest(time.time() - start_time)

            running = False
            break

        time.sleep(.001)

    pygame.display.quit()


if __name__ == '__main__':

    statistics = Statictics()
    set_user_settings()

    with open('user_settings.json', 'r') as file:
        r = json.load(file)
        work_duration = r.get('work_duration')
        rest_duration = r.get('rest_duration')

    start_time = time.time()

    while True:
    
        try:

            if time.time() - start_time >= work_duration:
                statistics.end_work(time.time() - start_time)

                rest(rest_duration)
                start_time = time.time()
            elif keyboard.is_pressed('ctrl+esc'):
                statistics.end_work(time.time() - start_time)

                rest(None)
                start_time = time.time()

        except KeyboardInterrupt:
            exit()

        except ImportError:
            print('ImportError. Проверьте root права')
            exit()

        except:
            traceback.print_exc()

        time.sleep(.01)
