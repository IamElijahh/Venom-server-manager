# ba_meta require api 9

import babase
import bauiv1 as bui
import bascenev1 as bs
import bauiv1lib.mainmenu
import weakref
import time
import json
import urllib.request
import urllib.parse
import threading

CURRENT_MOD_VERSION = 1.0 
DISCORD_INVITE_LINK = "https://discord.com/users/776813866599972865" # Or use your server link: https://discord.gg/yourcode

GITHUB_VERSION_URL = "https://raw.githubusercontent.com/IamElijahh/Venom-server-manager/main/version.txt"
GITHUB_CHANGELOG_URL = "https://raw.githubusercontent.com/IamElijahh/Venom-server-manager/main/changelog.txt"
GITHUB_NEW_ISSUE_URL = "https://github.com/IamElijahh/Venom-server-manager/issues/new"

_auto_join_state = {'timer': None, 'target': None}

class VenomDeveloperWindow(bui.Window):
    def __init__(self, main_window, transition: str = 'in_right'):
        self._main_window = weakref.ref(main_window)
        self._width = 650 
        self._height = 450
        
        saved_theme = babase.app.config.get('Venom_Theme', (0.08, 0.08, 0.1))
        self._root_widget = bui.containerwidget(size=(self._width, self._height), transition=transition, scale=1.1, color=saved_theme, on_cancel_call=self._close)
        super().__init__(self._root_widget)
        
        bui.textwidget(parent=self._root_widget, position=(self._width * 0.5, self._height - 60), size=(0, 0), h_align='center', v_align='center', text='DEVELOPER INFO', scale=1.5, color=(0.2, 0.8, 1.0))
        bui.textwidget(parent=self._root_widget, position=(self._width * 0.5, self._height - 110), size=(0, 0), h_align='center', v_align='center', text=f'Mod by Ayush (Venom) | Version {CURRENT_MOD_VERSION}', scale=0.9, color=(0.7, 0.7, 0.7))

        # "Slide into my DMs" Button
        bui.buttonwidget(parent=self._root_widget, position=(self._width * 0.5 - 150, self._height - 200), size=(300, 60), label='Slide into my DMs (Discord)', color=(0.3, 0.4, 0.9), on_activate_call=self._open_discord)

        # GitHub Support Buttons
        bui.buttonwidget(parent=self._root_widget, position=(80, self._height - 300), size=(220, 50), label='Report a Bug', color=(0.8, 0.3, 0.3), on_activate_call=self._open_bug_report)
        bui.buttonwidget(parent=self._root_widget, position=(350, self._height - 300), size=(220, 50), label='Patch Notes', color=(0.8, 0.6, 0.2), on_activate_call=self._open_changelog)

        bui.buttonwidget(parent=self._root_widget, position=(self._width * 0.5 - 60, 40), size=(120, 50), label='Close', color=(0.4, 0.4, 0.4), on_activate_call=self._close)

    def _open_discord(self):
        babase.open_url(DISCORD_INVITE_LINK)
        bui.screenmessage("Opening Discord...", color=(0.3, 0.4, 0.9))

    def _open_bug_report(self): bui.pushcall(lambda: VenomBugReportWindow())
    def _open_changelog(self): bui.pushcall(lambda: VenomChangelogWindow())
    def _close(self): bui.containerwidget(edit=self._root_widget, transition='out_right')


# --- IN-APP BUG REPORTER (Option A) ---
class VenomBugReportWindow(bui.Window):
    def __init__(self, transition: str = 'in_scale'):
        self._width = 800
        self._height = 450
        saved_theme = babase.app.config.get('Venom_Theme', (0.08, 0.08, 0.1))
        self._root_widget = bui.containerwidget(size=(self._width, self._height), transition=transition, scale=1.1, color=saved_theme, on_cancel_call=self._close)
        super().__init__(self._root_widget)
        
        bui.textwidget(parent=self._root_widget, position=(self._width * 0.5, self._height - 40), size=(0, 0), h_align='center', v_align='center', text='REPORT A BUG', scale=1.3, color=(0.8, 0.3, 0.3))
        bui.textwidget(parent=self._root_widget, position=(50, self._height - 100), size=(0, 0), text='Describe the issue. Clicking submit will open GitHub to securely post it:', scale=0.9, color=(0.8, 0.8, 0.8))

        self._input_field = bui.textwidget(parent=self._root_widget, position=(50, 110), size=(700, 200), text='', editable=True, max_chars=1000, description=bui.Lstr(value='What went wrong?'), v_align='top', h_align='left')

        bui.buttonwidget(parent=self._root_widget, position=(200, 40), size=(180, 50), label='Submit Report', color=(0.2, 0.8, 0.2), on_activate_call=self._submit)
        bui.buttonwidget(parent=self._root_widget, position=(420, 40), size=(180, 50), label='Cancel', color=(0.4, 0.4, 0.4), on_activate_call=self._close)

    def _submit(self):
        text = bui.textwidget(query=self._input_field).strip()
        if not text:
            bui.screenmessage("Please describe the bug first.", color=(1,0,0))
            return
        
        # URL encode the report and send directly to GitHub Issues page!
        title = urllib.parse.quote("In-Game Bug Report")
        body = urllib.parse.quote(f"**Mod Version:** {CURRENT_MOD_VERSION}\n**Description:**\n{text}")
        full_url = f"{GITHUB_NEW_ISSUE_URL}?title={title}&body={body}"
        
        babase.open_url(full_url)
        bui.screenmessage("Opening GitHub...", color=(0,1,0))
        self._close()

    def _close(self): bui.containerwidget(edit=self._root_widget, transition='out_scale')


# --- LIVE CHANGELOG FETCHER ---
class VenomChangelogWindow(bui.Window):
    def __init__(self, transition: str = 'in_scale'):
        self._width = 800
        self._height = 500
        saved_theme = babase.app.config.get('Venom_Theme', (0.08, 0.08, 0.1))
        self._root_widget = bui.containerwidget(size=(self._width, self._height), transition=transition, scale=1.1, color=saved_theme, on_cancel_call=self._close)
        super().__init__(self._root_widget)
        
        bui.textwidget(parent=self._root_widget, position=(self._width * 0.5, self._height - 40), size=(0, 0), h_align='center', v_align='center', text='LATEST PATCH NOTES', scale=1.3, color=(0.8, 0.6, 0.2))

        self._scroll = bui.scrollwidget(parent=self._root_widget, position=(50, 110), size=(700, 320), highlight=False)
        self._text = bui.textwidget(parent=self._scroll, position=(0,0), size=(680, 300), text='Fetching from GitHub...', editable=False, maxwidth=680, v_align='top', h_align='left', scale=0.8, color=(0.8,0.8,0.8))

        bui.buttonwidget(parent=self._root_widget, position=(self._width * 0.5 - 90, 30), size=(180, 50), label='Close', color=(0.4, 0.4, 0.4), on_activate_call=self._close)
        
        self._fetch_changelog()

    def _fetch_changelog(self):
        def fetch():
            try:
                req = urllib.request.Request(GITHUB_CHANGELOG_URL)
                with urllib.request.urlopen(req, timeout=3) as response:
                    data = response.read().decode('utf-8')
                    bui.pushcall(lambda: bui.textwidget(edit=self._text, text=data), from_other_thread=True)
            except Exception as e:
                bui.pushcall(lambda: bui.textwidget(edit=self._text, text=f"Failed to load patch notes.\n\nError: {e}"), from_other_thread=True)
        threading.Thread(target=fetch, daemon=True).start()

    def _close(self): bui.containerwidget(edit=self._root_widget, transition='out_scale')


# --- SETTINGS WINDOW ---
class VenomSettingsWindow(bui.Window):
    def __init__(self, main_window, transition: str = 'in_scale'):
        self._main_window = weakref.ref(main_window)
        self._width = 750 
        self._height = 550
        saved_theme = babase.app.config.get('Venom_Theme', (0.08, 0.08, 0.1))
        self._root_widget = bui.containerwidget(size=(self._width, self._height), transition=transition, scale=1.1, color=saved_theme, on_cancel_call=self._close)
        super().__init__(self._root_widget)
        
        bui.textwidget(parent=self._root_widget, position=(self._width * 0.5, self._height - 50), size=(0, 0), h_align='center', v_align='center', text='VENOM SETTINGS', scale=1.5, color=(0.5, 1.0, 0.5))
        bui.textwidget(parent=self._root_widget, position=(80, self._height - 130), size=(0, 0), text='UI Theme:', scale=1.1, color=(0.8, 0.8, 0.8))
        themes = [('Classic', (0.15, 0.25, 0.35)), ('Crimson', (0.4, 0.1, 0.1)), ('Moss', (0.15, 0.35, 0.15)), ('Dark', (0.08, 0.08, 0.1))]
        
        x_pos = 200
        for name, color in themes:
            bui.buttonwidget(parent=self._root_widget, position=(x_pos, self._height - 155), size=(110, 50), label=name, color=color, on_activate_call=lambda c=color: self._set_theme(c))
            x_pos += 120

        self._show_last_played = babase.app.config.get('Venom_Show_Time', True)
        self._categorize_time = babase.app.config.get('Venom_Categorize', False)

        bui.textwidget(parent=self._root_widget, position=(80, self._height - 230), size=(0, 0), text='Last Played Features:', scale=1.1, color=(0.8, 0.8, 0.8))
        self._cb1 = bui.checkboxwidget(parent=self._root_widget, position=(80, self._height - 290), size=(300, 40), text='Show Last Played Timestamps', value=self._show_last_played, on_value_change_call=self._toggle_time)
        self._cb2 = bui.checkboxwidget(parent=self._root_widget, position=(80, self._height - 350), size=(400, 40), text='Categorize Servers by Time (Disables Manual Sorting)', value=self._categorize_time, on_value_change_call=self._toggle_cat)

        bui.buttonwidget(parent=self._root_widget, position=(self._width * 0.5 - 75, 40), size=(150, 60), label='Done', color=(0.2, 0.8, 0.2), on_activate_call=self._close)

    def _set_theme(self, color):
        bui.containerwidget(edit=self._root_widget, color=color)
        babase.app.config['Venom_Theme'] = color
        babase.app.config.commit()
        bui.getsound('click01').play()
        mw = self._main_window()
        if mw and mw._root_widget.exists(): bui.containerwidget(edit=mw._root_widget, color=color)

    def _toggle_time(self, val):
        babase.app.config['Venom_Show_Time'] = val
        babase.app.config.commit()

    def _toggle_cat(self, val):
        babase.app.config['Venom_Categorize'] = val
        babase.app.config.commit()

    def _close(self):
        mw = self._main_window()
        if mw and mw._root_widget.exists(): mw._refresh_server_list()
        bui.containerwidget(edit=self._root_widget, transition='out_scale')


# --- SINGLE SERVER EXPORT PROMPT WINDOW ---
class VenomSingleExportPrompt(bui.Window):
    def __init__(self, server_dict, transition: str = 'in_scale'):
        self._width = 800
        self._height = 350
        saved_theme = babase.app.config.get('Venom_Theme', (0.08, 0.08, 0.1))
        self._root_widget = bui.containerwidget(size=(self._width, self._height), transition=transition, scale=1.1, color=saved_theme, on_cancel_call=self._close)
        super().__init__(self._root_widget)
        
        bui.textwidget(parent=self._root_widget, position=(self._width * 0.5, self._height - 40), size=(0, 0), h_align='center', v_align='center', text='EXPORT SERVER STRING', scale=1.3, color=(0.5, 1.0, 0.5))
        bui.textwidget(parent=self._root_widget, position=(self._width * 0.5, self._height - 80), size=(0, 0), h_align='center', v_align='center', text=f"For Server: {server_dict['name']}", scale=0.8, color=(0.6, 0.6, 0.6))

        try: self._server_string = " " + json.dumps({'name':server_dict['name'],'ip':server_dict['ip'],'port':server_dict['port']})
        except Exception as e: self._server_string = f" Export failed: {e}"

        scroll = bui.scrollwidget(parent=self._root_widget, position=(50, 110), size=(700, 150), highlight=False)
        bui.textwidget(parent=scroll, position=(0,0), size=(700,150), text=self._server_string, editable=False, maxwidth=680, v_align='top', h_align='left', scale=0.9, color=(0.8,0.8,0.8))

        bui.buttonwidget(parent=self._root_widget, position=(200, 30), size=(180, 50), label='Copy String', color=(0.8, 0.6, 0.2), on_activate_call=self._copy_string)
        bui.buttonwidget(parent=self._root_widget, position=(420, 30), size=(180, 50), label='Cancel', color=(0.4, 0.4, 0.4), on_activate_call=self._close)

    def _copy_string(self):
        try:
            babase.clipboard_set_text(self._server_string.strip())
            bui.screenmessage("Server string copied to clipboard!", color=(0,1,0))
            bui.getsound('ding').play()
            self._close()
        except Exception as e: bui.screenmessage(f"Copy failed: {e}", color=(1,0,0))

    def _close(self): bui.containerwidget(edit=self._root_widget, transition='out_scale')


# --- SINGLE SERVER IMPORT PROMPT WINDOW ---
class VenomSingleImportPrompt(bui.Window):
    def __init__(self, main_window, index, transition: str = 'in_scale'):
        self._main_window = weakref.ref(main_window)
        self._index = index
        self._width = 700
        self._height = 400
        saved_theme = babase.app.config.get('Venom_Theme', (0.08, 0.08, 0.1))
        self._root_widget = bui.containerwidget(size=(self._width, self._height), transition=transition, scale=1.1, color=saved_theme, on_cancel_call=self._close)
        super().__init__(self._root_widget)
        
        bui.textwidget(parent=self._root_widget, position=(self._width * 0.5, self._height - 40), size=(0, 0), h_align='center', v_align='center', text='IMPORT SINGLE SERVER SLOT', scale=1.3, color=(0.5, 1.0, 0.5))
        bui.textwidget(parent=self._root_widget, position=(self._width * 0.5, self._height - 80), size=(0, 0), h_align='center', v_align='center', text='WARNING: This will overwrite the current slot.', scale=0.8, color=(1.0, 0.2, 0.2))
        
        self._input_field = bui.textwidget(parent=self._root_widget, position=(50, 110), size=(600, 150), text='', editable=True, description=bui.Lstr(value='Paste string here (Ctrl+V)...'), v_align='top', h_align='left', scale=0.9)
        bui.buttonwidget(parent=self._root_widget, position=(150, 30), size=(180, 50), label='Overwrite Slot', color=(0.2, 0.6, 0.8), on_activate_call=self._confirm_import)
        bui.buttonwidget(parent=self._root_widget, position=(370, 30), size=(180, 50), label='Cancel', color=(0.4, 0.4, 0.4), on_activate_call=self._close)

    def _confirm_import(self):
        data = bui.textwidget(query=self._input_field).strip()
        if not data: return
        try:
            s = json.loads(data)
            if 'name' in s and 'ip' in s and 'port' in s and 0 <= self._index < len(babase.app.config['Venom_Servers_List']):
                s['last_played'] = babase.app.config['Venom_Servers_List'][self._index].get('last_played', 0)
                babase.app.config['Venom_Servers_List'][self._index] = s
                babase.app.config.commit()
                bui.screenmessage("Successfully imported into this slot!", color=(0,1,0))
                bui.getsound('shieldUp').play()
                mw = self._main_window()
                if mw and mw._root_widget.exists(): bui.pushcall(mw._refresh_server_list)
                self._close()
        except Exception: bui.screenmessage("Error: Text is not valid Venom server data.", color=(1,0,0))

    def _close(self): bui.containerwidget(edit=self._root_widget, transition='out_scale')


# --- MAIN MANAGER WINDOW ---
class VenomServerManagerWindow(bui.Window):
    def __init__(self, transition: str = 'in_right'):
        self._width = 1180 
        self._height = 700
        saved_theme = babase.app.config.get('Venom_Theme', (0.08, 0.08, 0.1))
        
        self._root_widget = bui.containerwidget(size=(self._width, self._height), transition=transition, scale=1.1, color=saved_theme, on_cancel_call=self._close)
        super().__init__(self._root_widget)
        
        self._close_button = bui.buttonwidget(parent=self._root_widget, position=(40, self._height - 80), size=(60, 60), label='X', color=(0.8, 0.2, 0.2), on_activate_call=self._close)
        bui.containerwidget(edit=self._root_widget, cancel_button=self._close_button)
        
        # Check for Live Updates on Launch!
        self._check_for_updates()

        bui.textwidget(parent=self._root_widget, position=(330, self._height - 110), size=(0, 0), text='Search List:', scale=0.8, color=(0.6,0.6,0.6))
        self._search_field = bui.textwidget(parent=self._root_widget, position=(430, self._height - 125), size=(200, 40), text='', editable=True, description=bui.Lstr(value='Search name or IP...'))
        bui.buttonwidget(parent=self._root_widget, position=(640, self._height - 125), size=(80, 40), label='Search', color=(0.2, 0.4, 0.8), on_activate_call=self._refresh_server_list)
        
        # Moved Settings and Dev buttons to the top right
        bui.buttonwidget(parent=self._root_widget, position=(self._width - 150, self._height - 90), size=(110, 50), label='Settings', color=(0.4, 0.4, 0.4), on_activate_call=self._open_settings)
        bui.buttonwidget(parent=self._root_widget, position=(self._width - 290, self._height - 90), size=(130, 50), label='Contact Dev', color=(0.2, 0.6, 0.8), on_activate_call=self._open_dev_menu)

        if 'Venom_Servers_List' not in babase.app.config: babase.app.config['Venom_Servers_List'] = []
        self._default_servers = [{'name': "🥊|DIVINE SUPER SMASH|🥊", 'ip': '80.225.198.251', 'port': 43210},{'name': "🧬⚡DIVINE VS ISHOWPP EPIC TEAMS⚡🧬", 'ip': '129.154.254.49', 'port': 43210},{'name': "⚽🏆 DIVINE EPIC SOCCER 🏆⚽", 'ip': '129.154.254.49', 'port': 43220},{'name': "🪨⚡𝗗𝗶𝘃𝗶𝗻𝗲 & 𝗦𝘁𝗼𝗻𝗲 𝗣𝗿𝗼'𝘀 𝗙𝗙𝗔⚡🪨", 'ip': '13.233.125.155', 'port': 43210}]

        # --- LEFT SIDE: ADD SERVER PANEL ---
        bui.textwidget(parent=self._root_widget, position=(110, self._height - 160), size=(0, 0), h_align='center', v_align='center', text='ADD SERVER', scale=0.9, color=(0.8, 0.8, 0.8))
        self._name_field = bui.textwidget(parent=self._root_widget, position=(30, self._height - 220), size=(160, 40), text='New Server', editable=True, maxwidth=140, color=(0.2, 1.0, 0.2))
        self._ip_field = bui.textwidget(parent=self._root_widget, position=(30, self._height - 280), size=(160, 40), text='192.168.1.1', editable=True, maxwidth=140)
        self._port_field = bui.textwidget(parent=self._root_widget, position=(30, self._height - 340), size=(160, 40), text='43210', editable=True, maxwidth=140)
        bui.buttonwidget(parent=self._root_widget, position=(40, self._height - 400), size=(140, 45), label='Save Server', color=(0.2, 0.8, 0.2), on_activate_call=self._add_server)

        # --- CENTER: SERVER BROWSER HEADERS ---
        bui.textwidget(parent=self._root_widget, position=(260, self._height - 170), size=(0, 0), text='NAME', scale=0.75, color=(0.5, 0.5, 0.5))
        bui.textwidget(parent=self._root_widget, position=(460, self._height - 170), size=(0, 0), text='ADDRESS', scale=0.75, color=(0.5, 0.5, 0.5))
        bui.textwidget(parent=self._root_widget, position=(670, self._height - 170), size=(0, 0), text='LAST PLAYED', scale=0.75, color=(0.5, 0.5, 0.5))
        bui.textwidget(parent=self._root_widget, position=(830, self._height - 170), size=(0, 0), text='ACTIONS', scale=0.75, color=(0.5, 0.5, 0.5))

        self._scroll_widget = bui.scrollwidget(
            parent=self._root_widget, position=(230, 90),
            size=(self._width - 250, self._height - 280), highlight=False
        )
        self._sub_container = None
        self._refresh_server_list()

        # --- BOTTOM BAR: IMPORT, EXPORT, AND MOD TITLE ---
        bui.buttonwidget(parent=self._root_widget, position=(230, 30), size=(200, 45), label='Import From Clipboard', color=(0.2, 0.6, 0.8), on_activate_call=self._import_all_bottom)
        bui.buttonwidget(parent=self._root_widget, position=(450, 30), size=(200, 45), label='Export All to Clipboard', color=(0.8, 0.6, 0.2), on_activate_call=self._export_all)
        bui.textwidget(parent=self._root_widget, position=(670, 50), size=(0, 0), text='MOD BY VENOM', scale=1.3, h_align='left', v_align='center', color=(0.5, 1.0, 0.5))

    # --- FEATURE 1: LIVE UPDATE CHECKER ---
    def _check_for_updates(self):
        def fetch():
            try:
                req = urllib.request.Request(GITHUB_VERSION_URL)
                with urllib.request.urlopen(req, timeout=2) as response:
                    latest_ver = float(response.read().decode('utf-8').strip())
                    if latest_ver > CURRENT_MOD_VERSION:
                        bui.pushcall(self._show_update_button, from_other_thread=True)
            except Exception: pass
        threading.Thread(target=fetch, daemon=True).start()

    def _show_update_button(self):
        if self._root_widget and self._root_widget.exists():
            bui.buttonwidget(parent=self._root_widget, position=(120, self._height - 80), size=(180, 50), label='UPDATE AVAILABLE!', color=(1.0, 0.5, 0.0), on_activate_call=self._open_dev_menu)

    def _open_settings(self): bui.pushcall(lambda: VenomSettingsWindow(self))
    def _open_dev_menu(self): bui.pushcall(lambda: VenomDeveloperWindow(self))

    def _add_server(self):
        name, ip, port = bui.textwidget(query=self._name_field), bui.textwidget(query=self._ip_field), bui.textwidget(query=self._port_field)
        if name and ip and port.isdigit():
            babase.app.config['Venom_Servers_List'].append({'name': name, 'ip': ip, 'port': int(port), 'last_played': 0})
            babase.app.config.commit() 
            bui.getsound('shieldUp').play()
            self._refresh_server_list()
        else: bui.screenmessage("Invalid Input! Ensure Port is a number.", color=(1,0,0))

    def _remove_server(self, index):
        if 0 <= index < len(babase.app.config['Venom_Servers_List']):
            del babase.app.config['Venom_Servers_List'][index]
            babase.app.config.commit()
            bui.getsound('shieldDown').play()
            self._refresh_server_list()

    def _move_server(self, index, direction):
        servers = babase.app.config['Venom_Servers_List']
        new_index = index + direction
        if 0 <= new_index < len(servers):
            servers[index], servers[new_index] = servers[new_index], servers[index]
            babase.app.config.commit()
            self._refresh_server_list()

    def _join_server(self, ip, port, index=None):
        bui.screenmessage(f"Connecting to {ip}:{port}...", color=(0, 1, 0))
        if index is not None and 0 <= index < len(babase.app.config['Venom_Servers_List']):
            babase.app.config['Venom_Servers_List'][index]['last_played'] = time.time()
            babase.app.config.commit()
        bs.connect_to_party(address=ip, port=port)
        _watch_for_real_server_name(ip, port, weakref.ref(self))

    def _toggle_auto_join(self, ip, port):
        global _auto_join_state
        if _auto_join_state['timer']:
            _auto_join_state['timer'], _auto_join_state['target'] = None, None
            bui.screenmessage("Auto-Join Cancelled.", color=(1, 0.2, 0.2))
        else:
            bui.screenmessage(f"AUTO-JOIN: Spamming {ip}:{port}...", color=(0.2, 1.0, 0.2))
            _auto_join_state['target'] = (ip, port)
            def spam_func():
                if _auto_join_state['timer']: bs.connect_to_party(address=ip, port=port)
            _auto_join_state['timer'] = babase.AppTimer(4.0, spam_func, repeat=True)
            bs.connect_to_party(address=ip, port=port)
            _watch_for_real_server_name(ip, port, weakref.ref(self))

    def _export_single_row(self, server_dict): bui.pushcall(lambda: VenomSingleExportPrompt(server_dict))
    def _import_server_to_row(self, index): bui.pushcall(lambda: VenomSingleImportPrompt(self, index))

    def _export_all(self):
        try:
            clean_list = [{'name':s['name'],'ip':s['ip'],'port':s['port']} for s in babase.app.config.get('Venom_Servers_List', [])]
            babase.clipboard_set_text(json.dumps(clean_list))
            bui.screenmessage("ALL Servers copied to clipboard!", color=(0,1,0))
            bui.getsound('ding').play()
        except Exception as e: bui.screenmessage(f"Export failed: {e}", color=(1,0,0))

    def _import_all_bottom(self):
        try:
            data = babase.clipboard_get_text()
            if not data: return
            new_servers = json.loads(data)
            if isinstance(new_servers, dict): new_servers = [new_servers]
            if isinstance(new_servers, list):
                count = 0
                for s in new_servers:
                    if 'name' in s and 'ip' in s and 'port' in s:
                        s['last_played'] = s.get('last_played', 0)
                        babase.app.config['Venom_Servers_List'].append(s)
                        count += 1
                babase.app.config.commit()
                bui.screenmessage(f"Imported {count} servers!", color=(0,1,0))
                bui.getsound('shieldUp').play()
                self._refresh_server_list()
        except Exception: bui.screenmessage("Invalid Venom JSON data in clipboard.", color=(1,0,0))

    def _format_time(self, timestamp):
        if not timestamp or timestamp == 0: return "Never"
        diff = time.time() - timestamp
        if diff < 86400: return "Today"
        return f"{int(diff/86400)} days ago" if diff < 604800 else "Older"

    def _refresh_server_list(self):
        if self._sub_container and self._sub_container.exists(): self._sub_container.delete()
        search = bui.textwidget(query=self._search_field).strip().lower()
        all_user_servers = babase.app.config.get('Venom_Servers_List', [])
        filtered_users = [(i, s) for i, s in enumerate(all_user_servers) if search in s['name'].lower() or search in s['ip'].lower()]
        show_time, categorize = babase.app.config.get('Venom_Show_Time', True), babase.app.config.get('Venom_Categorize', False)
        
        row_width = 850 
        self._sub_container = bui.columnwidget(parent=self._scroll_widget, size=(row_width, max(50, (len(self._default_servers) + len(filtered_users) + 4) * 60)))

        def draw_row(s, index=None, is_default=False):
            row = bui.rowwidget(parent=self._sub_container, size=(row_width, 60))
            
            bui.textwidget(parent=row, size=(200, 50), text=s['name'], v_align='center', maxwidth=190, color=(1.0, 0.8, 0.2) if is_default else (0.8,0.8,0.8), scale=0.8) 
            bui.textwidget(parent=row, size=(210, 50), text=f"{s['ip']}:{s['port']}", v_align='center', maxwidth=200, color=(0.7, 0.7, 1.0), scale=0.8)
            
            time_txt = self._format_time(s.get('last_played', 0)) if show_time and not is_default else ""
            bui.textwidget(parent=row, size=(90, 50), text=time_txt, v_align='center', maxwidth=80, color=(0.5, 0.5, 0.5), scale=0.7)
            bui.textwidget(parent=row, size=(10, 50), text="")
            
            if not is_default:
                bui.buttonwidget(parent=row, size=(40, 35), label='Imp', color=(0.2, 0.6, 0.8), scale=0.8, on_activate_call=lambda idx=index: self._import_server_to_row(idx))
                bui.buttonwidget(parent=row, size=(40, 35), label='Exp', color=(0.8, 0.6, 0.2), scale=0.8, on_activate_call=lambda s=s: self._export_single_row(s))
            else: bui.textwidget(parent=row, size=(80, 50), text="") 
                
            bui.textwidget(parent=row, size=(10, 50), text="")

            bui.buttonwidget(parent=row, size=(75, 35), label='Connect', color=(0.2, 0.8, 0.2), scale=0.8, on_activate_call=lambda ip=s['ip'], p=s['port'], idx=index: self._join_server(ip, p, idx))
            bui.buttonwidget(parent=row, size=(50, 35), label='Auto', color=(0.8, 0.2, 0.8), scale=0.8, on_activate_call=lambda ip=s['ip'], p=s['port']: self._toggle_auto_join(ip, p))
            
            bui.textwidget(parent=row, size=(10, 50), text="")
            
            if is_default:
                bui.textwidget(parent=row, size=(105, 50), text="[DEFAULT]", v_align='center', h_align='center', color=(0.5, 0.5, 0.5), scale=0.7)
            else:
                if not categorize and search == "":
                    bui.buttonwidget(parent=row, size=(35, 35), label='^', color=(0.4, 0.4, 0.4), scale=0.8, on_activate_call=lambda idx=index: self._move_server(idx, -1))
                    bui.buttonwidget(parent=row, size=(35, 35), label='v', color=(0.4, 0.4, 0.4), scale=0.8, on_activate_call=lambda idx=index: self._move_server(idx, 1))
                else: bui.textwidget(parent=row, size=(70, 50), text="")

                bui.buttonwidget(parent=row, size=(35, 35), label='X', color=(0.8, 0.2, 0.2), scale=0.8, on_activate_call=lambda idx=index: self._remove_server(idx))

        if search == "":
            for s in self._default_servers: draw_row(s, is_default=True)

        if categorize and search == "":
            cat_today = [x for x in filtered_users if self._format_time(x[1].get('last_played',0)) == "Today"]
            cat_week = [x for x in filtered_users if "days ago" in self._format_time(x[1].get('last_played',0))]
            cat_older = [x for x in filtered_users if self._format_time(x[1].get('last_played',0)) in ["Older", "Never"]]
            
            if cat_today:
                bui.textwidget(parent=self._sub_container, size=(row_width, 40), text="--- PLAYED TODAY ---", h_align='center', v_align='center', color=(0.4,0.8,0.4))
                for idx, s in cat_today: draw_row(s, idx)
            if cat_week:
                bui.textwidget(parent=self._sub_container, size=(row_width, 40), text="--- PLAYED THIS WEEK ---", h_align='center', v_align='center', color=(0.8,0.8,0.4))
                for idx, s in cat_week: draw_row(s, idx)
            if cat_older:
                bui.textwidget(parent=self._sub_container, size=(row_width, 40), text="--- OLDER / NEVER ---", h_align='center', v_align='center', color=(0.8,0.4,0.4))
                for idx, s in cat_older: draw_row(s, idx)
        else:
            for idx, s in filtered_users: draw_row(s, idx)

    def _close(self): bui.containerwidget(edit=self._root_widget, transition='out_right')


# --- RECURRING AUTO-NAME UPDATER ---
def _watch_for_real_server_name(target_ip, target_port, win_weakref):
    state = {'attempts': 0, 'timer': None}
    def check_name():
        state['attempts'] += 1
        if state['attempts'] > 15:
            state['timer'] = None 
            return
        try:
            info = bs.get_connection_to_host_info_2()
            if info and hasattr(info, 'name'):
                real_name = info.name
                if real_name and real_name.strip():
                    global _auto_join_state
                    if _auto_join_state['timer']:
                        _auto_join_state['timer'], _auto_join_state['target'] = None, None
                        bui.getsound('shieldUp').play()
                    
                    servers = babase.app.config.get('Venom_Servers_List', [])
                    updated = False
                    for s in servers:
                        if s['ip'] == target_ip and s['port'] == target_port and s['name'] != real_name:
                            s['name'] = real_name 
                            updated = True
                    if updated:
                        babase.app.config.commit()
                        win = win_weakref()
                        if win and win._root_widget.exists(): bui.pushcall(win._refresh_server_list)
                        state['timer'] = None
        except Exception: pass 
    state['timer'] = babase.AppTimer(2.0, check_name, repeat=True)

# --- UI INJECTION LOGIC ---
_old_main_menu_refresh = bauiv1lib.mainmenu.MainMenuWindow._refresh
def _new_main_menu_refresh(self):
    _old_main_menu_refresh(self)
    if hasattr(self, '_root_widget') and self._root_widget:
        bui.buttonwidget(parent=self._root_widget, position=(60, 60), size=(180, 50), label='Venom Servers', color=(0.1, 0.8, 0.2), on_activate_call=self._open_venom_ui)
def _open_venom_ui(self): bui.pushcall(VenomServerManagerWindow)
bauiv1lib.mainmenu.MainMenuWindow._refresh = _new_main_menu_refresh
bauiv1lib.mainmenu.MainMenuWindow._open_venom_ui = _open_venom_ui

# ba_meta export babase.Plugin
class VenomServerMod(babase.Plugin):
    def on_app_running(self): pass