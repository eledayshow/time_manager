import pygame
from pygame.font import Font
from pygame.color import Color
import pyautogui
import time
import conf
import random


pygame.init()
SCREEN_INFO = pygame.display.Info()
SCREEN_W, SCREEN_H = SCREEN_INFO.current_w, SCREEN_INFO.current_h
vh, vw = SCREEN_H / 100, SCREEN_W / 100


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


def rest():
    start_time = time.time()

    pyautogui.screenshot().save(conf.screenshot_path)
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)

    image = pygame.image.load(conf.screenshot_path).convert_alpha()
    image = pygame.transform.scale(image, (SCREEN_W, SCREEN_H))

    image_alpha = 255
    text_alpha = 0

    title = 'Перерыв'

    running = True
    while running:
        
        subtitle = time_to_str(conf.rest_duration - (time.time() - start_time))

        if time.time() - start_time >= conf.rest_duration:
            return
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        image.set_alpha(image_alpha)

        f_t = Font(conf.title_font_path, 62)
        f_st = Font(conf.subtitle_font_path, 20)

        wrapped_title = wrap_text(title, f_t, conf.max_width_title * vw)
        wrapped_subtitle = wrap_text(subtitle, f_st, conf.max_width_subtitle * vw)

        total_height_title = sum(f_t.size(line)[1] for line in wrapped_title)
        total_height_subtitle = sum(f_st.size(line)[1] for line in wrapped_subtitle)
        
        total_height = total_height_title + total_height_subtitle
        y_start = (SCREEN_H - total_height) // 2

        title_rects = []
        subtitle_rects = []

        pygame.draw.rect(
            screen, Color(conf.bg_pg_color), 
            pygame.Rect(0, 0, SCREEN_W * ((time.time() - start_time) / conf.rest_duration), SCREEN_H)
        )

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
        time.sleep(.001)

    pygame.quit()


rest()