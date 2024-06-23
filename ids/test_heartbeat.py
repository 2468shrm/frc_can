
from heartbeat import HeartBeatMsg
from struct import pack_into


if __name__ == "__main__":
    if True:
        hb = HeartBeatMsg()
        hb.time_of_day_hr = 0x1f
        print(f"hb: {hb}\n\n")
        del(hb)
        hb = HeartBeatMsg()
        hb.time_of_day_min = 0x3f
        print(f"hb: {hb}\n\n")
        del(hb)
        hb = HeartBeatMsg()
        hb.time_of_day_sec = 0x3f
        print(f"hb: {hb}\n\n")
        del(hb)

    if True:
        hb = HeartBeatMsg()
        hb.time_of_day_day = 0x1f
        print(f"hb: {hb}\n\n")
        del(hb)
        hb = HeartBeatMsg()
        hb.time_of_day_month = 0xf
        print(f"hb: {hb}\n\n")
        del(hb)
        hb = HeartBeatMsg()
        hb.time_of_day_year = 0x3f
        print(f"hb: {hb}\n\n")
        del(hb)

    if True:
        hb = HeartBeatMsg()
        hb.tournament_type = 0x3f
        print(f"hb: {hb}\n\n")
        del(hb)
        hb = HeartBeatMsg()
        hb.system_watchdog = 1
        print(f"hb: {hb}\n\n")
        del(hb)
        hb = HeartBeatMsg()
        hb.test_mode = 1
        print(f"hb: {hb}\n\n")
        del(hb)
        hb = HeartBeatMsg()
        hb.autonomous = 1
        print(f"hb: {hb}\n\n")
        del(hb)
        hb = HeartBeatMsg()
        hb.enabled = 1
        print(f"hb: {hb}\n\n")
        del(hb)
        hb = HeartBeatMsg()
        hb.red_alliance = 1
        print(f"hb: {hb}\n\n")
        del(hb)

    if True:
        hb = HeartBeatMsg()
        hb.replay_number = 0x3f
        print(f"hb: {hb}\n\n")
        del(hb)
        hb = HeartBeatMsg()
        hb.match_number = 0x3ff
        print(f"hb: {hb}\n\n")
        del(hb)
        hb = HeartBeatMsg()
        hb.match_time = 0xff
        print(f"hb: {hb}\n\n")
        del(hb)

    if True:
        buff = bytearray(8)

        alignment = 0x0102030405060708
        extracted_alignment = pack_into(">Q", buff, 0, alignment)
        print(f"alignment: {alignment:x} buff: {buff}\n\n")

        time_of_day_hr = 0xf800000000000000
        extracted_time_of_day_hr = pack_into(">Q", buff, 0, time_of_day_hr)
        print(f"time_of_day_hr: {time_of_day_hr:x} buff: {buff}\n\n")

        hb = HeartBeatMsg()
        print(f"heartbeat (<empty>): {hb.data}")
        hb.match_time = 0xff
        print(f"heartbeat (+match_time): {hb.data}")
        hb.enabled = 1
        print(f"heartbeat (+enabled): {hb.data}")
        hb.system_watchdog = 1
        print(f"heartbeat (+system_watchdog): {hb.data}")
        hb.red_alliance = 1
        print(f"heartbeat (+red_alliance): {hb.data}")
        hb.autonomous = 1
        print(f"heartbeat (+autonomous): {hb.data}")
        hb.test_mode = 1
        print(f"heartbeat (+test_mode): {hb.data}")
        hb.tournament_type = 7
        print(f"heartbeat (+tournament_type): {hb.data}")
        hb.replay_number = 0x3f
        print(f"heartbeat (+replay_number): {hb.data}")
        hb.match_number = 0x3ff
        print(f"heartbeat (+match_number): {hb.data}")

        hb.time_of_day_year = 0x3f
        print(f"heartbeat (+time_of_day_year): {hb.data}")
        hb.time_of_day_month = 0xf
        print(f"heartbeat (+time_of_day_month): {hb.data}")
        hb.time_of_day_day = 0x1f
        print(f"heartbeat (+time_of_day_day): {hb.data}")
        hb.time_of_day_sec = 0x3f
        print(f"heartbeat (+time_of_day_sec): {hb.data}")
        hb.time_of_day_min = 0x3f
        print(f"heartbeat (+time_of_day_min): {hb.data}")
        hb.time_of_day_hr = 0x1f
        print(f"heartbeat (+time_of_day_hr): {hb.data}")

        hb_seq = HeartBeatMsg()
        hb_seq.match_time = 0
        hb_seq.system_watchdog = 1
        hb_seq.match_number = 21
        print(f"hb_seq: {hb_seq.data}")

        hb_seq.match_time = hb_seq.match_time + 1
        print(f"hb_seq: {hb_seq.data}")

        hb_seq.match_time = hb_seq.match_time + 1
        print(f"hb_seq: {hb_seq.data}")

        hb_seq.match_time = hb_seq.match_time + 1
        print(f"hb_seq: {hb_seq.data}")

        hb_seq.match_time += 1
        print(f"hb_seq: {hb_seq.data}")

