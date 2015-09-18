#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psutil, time
from pywiring.i2c import LCDBackpack
from liquidcrystal import LiquidCrystal

full_ch_num = lambda val, chnum: int(round(chnum/100.*val))

def format_size(b):
    if b <= 999:
        return str(int(b)) + "B"
    kb = b / 1024.
    if kb <= 999:
        return str(int(kb)) + "K"
    mb = kb / 1024.
    if mb > 999:
        return str(round(mb/1024., 1)) + "G"
    else:
        return str(int(mb)) + "M"

def create_custom_chars(lcd):
    c0 = [3, 4, 9, 11, 11, 9, 4, 3]    # start full
    c1 = [24, 4, 18, 26, 26, 18, 4, 24]  # end full
    c2 = [3, 4, 8, 8, 8, 8, 4, 3]    # start empty
    c3 = [24, 4, 2, 2, 2, 2, 4, 24]      # end empty
    c4 = [31, 0, 31, 31, 31, 31, 0, 31]  # mid full
    c5 = [31, 0, 0, 0, 0, 0, 0, 31]      # mid empty
    c6 = [31, 0, 28, 30, 30, 28, 0, 31]  # mid end
    c7 = [31, 0, 16, 24, 24, 16, 0, 31]    # start-end
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

def get_bytes(t, iface='wlan0'):
    with open('/sys/class/net/' + iface + '/statistics/' + t + '_bytes', 'r') as f:
        data = f.read()
    return int(data)

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
        if full == avail or full == avail -1:
            lcd.move_cursor_left()
        if full == avail:
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
                #create_custom_chars(lcd)
                # prev_cpu_full = -1
                # prev_mem_full = -1
                # while True:
                #     cpu_p = psutil.cpu_percent(0.3)
                #     mem_u = psutil.phymem_usage()
                #     cpu_s = "{:>3}%".format(str(int(cpu_p)))# + "%"
                #     mem_s = format_size(mem_u.used)

                #     avail_c_c = 15 - 4 #- len(cpu_s)
                #     full_c = full_ch_num(cpu_p, avail_c_c)
                #     lcd.home()
                #     if not full_c == prev_cpu_full:
                #         lcd.print_str("C")#write(6) # cpu
                #         print_bar(full_c, avail_c_c, [0, 1], full_c < prev_cpu_full)
                #         lcd.print_str(cpu_s)
                #         prev_cpu_full = full_c

                #     avail_c_m = 15 - len(mem_s)
                #     full_c = full_ch_num(mem_u.percent, avail_c_m)
                #     if not full_c == prev_mem_full:
                #         lcd.set_cursor(1, 0)
                #         lcd.print_str("M")#write(7) # mem
                #         print_bar(full_c, avail_c_m, [1, 1], full_c < prev_mem_full)
                #         lcd.print_str(mem_s)
                #         prev_mem_full = full_c

                    # time.sleep(0.3)

                prev_t = time.time()
                prev_tx = get_bytes("tx")
                prev_rx = get_bytes("rx")
                io = psutil.disk_io_counters()
                prev_dx = io.read_bytes + io.write_bytes

                while True:
                    cpu_p = psutil.cpu_percent(0.3)
                    mem_u = psutil.phymem_usage()
                    cpu_s = "{:>3}%".format(str(int(cpu_p)))
                    mem_s = format_size(mem_u.used)
                    tx = get_bytes("tx")
                    rx = get_bytes("rx")
                    t = time.time()
                    st = (tx - prev_tx) / (t - prev_t)
                    sr = (rx - prev_rx) / (t - prev_t)
                    io = psutil.disk_io_counters()
                    dx = io.read_bytes + io.write_bytes
                    sd = (dx - prev_dx) / (t - prev_t)
                    disk_s = format_size(sd)
                    prev_tx = tx
                    prev_rx = rx
                    prev_dx = dx
                    prev_t = t

                    lcd.home()
                    lcd.write(0b11000110) # ↓
                    lcd.print_str(format_size(sr) + "  ")

                    lcd.set_cursor(0, 7)
                    lcd.write(0b11000101) # ↑
                    lcd.print_str(format_size(st) + "  ")

                    lcd.set_cursor(0, 12)
                    lcd.print_str(cpu_s + "    ")

                    lcd.set_cursor(1, 0)
                    lcd.print_str("m " + mem_s)

                    lcd.set_cursor(1, 7)
                    lcd.print_str(" i/o {:>4}  ".format(disk_s))




            except IOError:
                time.sleep(1)
                continue
    except KeyboardInterrupt:
        raise SystemExit