# -*- coding: utf-8 -*-
#
# Copyright (c) 2015 by Simmo Saan <simmo.saan@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

#
# History:
#
# 2015-08-25, Simmo Saan <simmo.saan@gmail.com>
#   version 0.2: add bar item for indication
# 2015-08-25, Simmo Saan <simmo.saan@gmail.com>
#   version 0.1: initial script
#

"""
Filter buffers automatically while searching them
"""

from __future__ import print_function

SCRIPT_NAME = "grep_filter"
SCRIPT_AUTHOR = "Simmo Saan <simmo.saan@gmail.com>"
SCRIPT_VERSION = "0.2"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "Filter buffers automatically while searching them"

IMPORT_OK = True

try:
	import weechat
except ImportError:
	print("This script must be run under WeeChat.")
	print("Get WeeChat now at: http://www.weechat.org/")
	IMPORT_OK = False

def get_merged_buffers(ptr):
	hdata = weechat.hdata_get("buffer")
	buffers = weechat.hdata_get_list(hdata, "gui_buffers")
	buffer = weechat.hdata_search(hdata, buffers, "${buffer.number} == %i" % weechat.hdata_integer(hdata, ptr, "number"), 1)
	nbuffer = weechat.hdata_move(hdata, buffer, 1)

	ret = []
	while buffer:
		ret.append(weechat.hdata_string(hdata, buffer, "full_name"))

		if (weechat.hdata_integer(hdata, buffer, "number") == weechat.hdata_integer(hdata, nbuffer, "number")):
			buffer = nbuffer
			nbuffer = weechat.hdata_move(hdata, nbuffer, 1)
		else:
			buffer = None

	return ret

def filter_exists(name):
	hdata = weechat.hdata_get("filter")
	filters = weechat.hdata_get_list(hdata, "gui_filters")
	filter = weechat.hdata_search(hdata, filters, "${filter.name} == %s" % name, 1)

	return bool(filter)

def filter_del(name):
	weechat.command(weechat.buffer_search_main(), "/filter del %s" % name)

def filter_addreplace(name, buffers, tags, regex):
	if filter_exists(name):
		filter_del(name)

	weechat.command(weechat.buffer_search_main(), "/filter add %s %s %s %s" % (name, buffers, tags, regex))

def buffer_searching(ptr):
	hdata = weechat.hdata_get("buffer")

	return bool(weechat.hdata_integer(hdata, ptr, "text_search"))

def input_search_cb(data, signal, signal_data):
	hdata = weechat.hdata_get("buffer")

	buffers = ",".join(get_merged_buffers(signal_data))
	name = "%s_%s" % (SCRIPT_NAME, buffers)

	if buffer_searching(signal_data):
		filter_addreplace(name, buffers, "*", "!")
	else:
		filter_del(name)
	
	weechat.bar_item_update(SCRIPT_NAME)

	return weechat.WEECHAT_RC_OK

def input_text_changed_cb(data, signal, signal_data):
	hdata = weechat.hdata_get("buffer")

	if buffer_searching(signal_data):
		buffers = ",".join(get_merged_buffers(signal_data))
		name = "%s_%s" % (SCRIPT_NAME, buffers)
		regex = weechat.hdata_string(hdata, signal_data, "input_buffer")

		filter_addreplace(name, buffers, "*", "!%s" % regex)

	return weechat.WEECHAT_RC_OK

def bar_item_build(data, item, window, buffer, extra_info):
	buffers = ",".join(get_merged_buffers(buffer))
	name = "%s_%s" % (SCRIPT_NAME, buffers)

	if filter_exists(name):
		return "grep"
	else:
		return ""

if __name__ == "__main__" and IMPORT_OK:
	if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
		weechat.hook_signal("input_search", "input_search_cb", "")
		weechat.hook_signal("input_text_changed", "input_text_changed_cb", "")

		weechat.bar_item_new("(extra)%s" % SCRIPT_NAME, "bar_item_build", "")

