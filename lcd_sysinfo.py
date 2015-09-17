#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psutil, time
from pywiring.i2c import LCDBackpack
from liquidcrystal import LiquidCrystal

full_ch_num = lambda val, chnum: int(round(chnum/100.*val))

def format_size(b):
    mb = b / 1024. / 1024.
    if mb > 999:
        return str(round(mb/1024., 1)) + "G"
    else:
        return str(int(mb)) + "M"

def create_custom_chars(lcd):
    c0 = [7, 8, 19, 23, 23, 19, 8, 7]    # start full
    c1 = [28, 2, 25, 29, 29, 25, 2, 28]  # end full
    c2 = [7, 8, 16, 16, 16, 16, 8, 7]    # start empty
    c3 = [28, 2, 1, 1, 1, 1, 2, 28]      # end empty
    c4 = [31, 0, 31, 31, 31, 31, 0, 31]  # mid full
    c5 = [31, 0, 0, 0, 0, 0, 0, 31]      # mid empty
    c6 = [31, 0, 28, 30, 30, 28, 0, 31]  # mid end
    c7 = [31, 0, 0, 16, 16, 0, 0, 31]    # start-end
    # c7 = [7, 8, 18, 23, 23, 18, 8, 7]    # start-end
    # c6 = [0, 14, 25, 23, 23, 25, 14, 0]  # cpu
    # c7 = [0, 14, 21, 17, 21, 21, 14, 0]  # mem

    lcd.create_char(0, c0)
    lcd.create_char(1, c1)
    lcd.create_char(2, c2)
    lcd.create_char(3, c3)
    lcd.create_char(4, c4)
    lcd.create_char(5, c5)
    lcd.create_char(6, c6)
    lcd.create_char(7, c7)
    lcd.clear()

def print_bar(full, avail, cur_pos=[0, 0], reverse=False):
    if not reverse:
        # if full == 1:
        #   lcd.write(7) # start-end
        if full > 0:
            lcd.write(0) # start full
        else:
            lcd.write(2) # start empty
        for i in xrange(0, full-1):
            lcd.write(4) # mid full
        if full > 1 and full < avail:
            lcd.write(6) # mid end
        if full == 1:
            lcd.write(7) # start-end
        for i in xrange(0, avail - full - 2):
            lcd.write(5) # mid empty
        if full == avail:
            lcd.move_cursor_left()
            lcd.write(1) # end full
        else:
            lcd.write(3) # end empty
    else:
        row = cur_pos[0]
        col = cur_pos[1]
        lcd.set_cursor(row, col + avail - 1)
        lcd.rtl = True
        if full == avail:
            lcd.write(1) # end full
        else:
            lcd.write(3) # end empty
        for i in xrange(0, avail - full - 2):
            lcd.write(5) # mid empty
        if full == 1:
            lcd.write(7) # start-end
        if full > 1 and full < avail:
            lcd.write(6) # mid end
        for i in xrange(0, full-1):
            lcd.write(4) # mid full
        if full == avail:
            lcd.move_cursor_right()
        # if full == 1:
        #   lcd.write(7) # start-end
        if full > 0:
            lcd.write(0) # start full
        else:
            lcd.write(2) # start empty
        lcd.set_cursor(row, col + avail)
        lcd.ltr = True

if __name__ == "__main__":
    try:
        while True:
            try:
                ioi = LCDBackpack(1, 0x27)
                lcd = LiquidCrystal(ioi)
                create_custom_chars(lcd)
                prev_cpu_full = -1
                prev_mem_full = -1
                while True:
                    cpu_p = psutil.cpu_percent(0.1)
                    mem_u = psutil.phymem_usage()
                    cpu_s = str(int(cpu_p)) + "%"
                    mem_s = format_size(mem_u.used)

                    avail_c_c = 15 - len(cpu_s)
                    full_c = full_ch_num(cpu_p, avail_c_c)
                    lcd.home()
                    if not full_c == prev_cpu_full:
                        lcd.print_str("C")#write(6) # cpu
                        print_bar(full_c, avail_c_c, [0, 1], full_c < prev_cpu_full)
                        lcd.print_str(cpu_s)
                        prev_cpu_full = full_c

                    avail_c_m = 15 - len(mem_s)
                    full_c = full_ch_num(mem_u.percent, avail_c_m)
                    if not full_c == prev_mem_full:
                        lcd.set_cursor(1, 0)
                        lcd.print_str("M")#write(7) # mem
                        print_bar(full_c, avail_c_m, [1, 1], full_c < prev_mem_full)
                        lcd.print_str(mem_s)
                        prev_mem_full = full_c

                    time.sleep(0.3)
            except IOError:
                time.sleep(1)
                continue
    except KeyboardInterrupt:
        raise SystemExit