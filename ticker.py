import time


def should_report():
	global last_report_tm
	ct = time.time()
	if (last_report_tm is None) or (ct - last_report_tm > 1):
		last_report_tm = ct
		return True
	else:
		return False


last_report_tm = None
