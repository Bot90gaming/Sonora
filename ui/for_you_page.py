"""Personalized YouTube Music recommendations."""
from __future__ import annotations
import logging
import threading

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

from core.api import MusicAPI
from ui.widgets import load_picture_async, make_track_list, thumbnail_url

logger = logging.getLogger(__name__)


class ForYouPage(Gtk.Box):
    def __init__(
        self,
        api: MusicAPI,
        on_play,
        on_queue,
        on_download=None,
        on_play_all=None,
    ):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.api = api
        self.on_play = on_play
        self.on_queue = on_queue
        self.on_download = on_download
        self.on_play_all = on_play_all
        self._authenticated = False
        self._load_id = 0
        self._build()
        self._show_status(
            "Your mix, made for you",
            "Sign in with YouTube Music request headers to load recommendations.",
            "emblem-music-symbolic",
        )

    def _build(self):
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.set_margin_top(12)
        header.set_margin_bottom(12)
        header.set_margin_start(16)
        header.set_margin_end(16)

        title = Gtk.Label(label="For You")
        title.add_css_class("title-2")
        title.set_halign(Gtk.Align.START)
        title.set_hexpand(True)
        header.append(title)

        refresh = Gtk.Button()
        refresh.set_icon_name("view-refresh-symbolic")
        refresh.set_tooltip_text("Refresh recommendations")
        refresh.add_css_class("flat")
        refresh.add_css_class("circular")
        refresh.connect("clicked", lambda *_: self.refresh())
        header.append(refresh)
        self.append(header)
        self.append(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL))

        self._content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._content.set_vexpand(True)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)
        scroll.set_child(self._content)
        self.append(scroll)

    def set_api(self, api: MusicAPI, authenticated: bool):
        self.api = api
        self._authenticated = authenticated
        self.refresh()

    def refresh(self):
        self._load_id += 1
        load_id = self._load_id
        if not self._authenticated:
            self._show_status(
                "Sign in to get recommendations",
                "Use the account button to sign in with YouTube Music request headers.",
                "avatar-default-symbolic",
            )
            return

        self._show_spinner()

        def _fetch():
            try:
                sections = self.api.get_home(limit=6)
                GLib.idle_add(self._show_sections, sections, load_id)
            except Exception as exc:
                logger.exception("Could not load YouTube Music recommendations")
                GLib.idle_add(self._show_error, str(exc), load_id)

        threading.Thread(target=_fetch, daemon=True).start()

    def _clear_content(self):
        child = self._content.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self._content.remove(child)
            child = next_child

    def _show_status(self, title: str, description: str, icon: str):
        self._clear_content()
        page = Adw.StatusPage()
        page.set_icon_name(icon)
        page.set_title(title)
        page.set_description(description)
        page.set_vexpand(True)
        self._content.append(page)

    def _show_spinner(self):
        self._clear_content()
        spinner = Gtk.Spinner()
        spinner.set_size_request(48, 48)
        spinner.set_halign(Gtk.Align.CENTER)
        spinner.set_valign(Gtk.Align.CENTER)
        spinner.set_vexpand(True)
        spinner.start()
        self._content.append(spinner)

    def _show_sections(self, sections: list[dict], load_id: int):
        if load_id != self._load_id:
            return
        self._clear_content()
        if not sections:
            self._show_status(
                "No recommendations yet",
                "Try refreshing later, or listen to more music on YouTube Music.",
                "edit-find-symbolic",
            )
            return

        for section in sections:
            contents = section.get("contents") or []
            if not contents:
                continue

            heading = Gtk.Label(label=section.get("title", "Recommended"))
            heading.add_css_class("title-3")
            heading.set_halign(Gtk.Align.START)
            heading.set_margin_top(16)
            heading.set_margin_bottom(8)
            heading.set_margin_start(16)
            heading.set_margin_end(16)
            self._content.append(heading)

            grid = Gtk.FlowBox()
            grid.set_selection_mode(Gtk.SelectionMode.NONE)
            grid.set_min_children_per_line(1)
            grid.set_max_children_per_line(4)
            grid.set_row_spacing(12)
            grid.set_column_spacing(12)
            grid.set_homogeneous(True)
            grid.set_margin_start(12)
            grid.set_margin_end(12)

            for item in contents:
                card = self._recommendation_card(item)
                if card:
                    grid.insert(card, -1)

            if grid.get_first_child():
                self._content.append(grid)
            else:
                self._content.remove(heading)

        if self._content.get_first_child() is None:
            self._show_status(
                "No playable recommendations",
                "YouTube Music did not return any recommendations this time.",
                "edit-find-symbolic",
            )

    def _recommendation_card(self, item: dict) -> Gtk.FlowBoxChild | None:
        title = item.get("title") or item.get("name") or "Unknown"
        video_id = item.get("videoId")
        playlist_id = item.get("playlistId")
        browse_id = item.get("browseId")
        result_type = (item.get("resultType") or "").lower()
        route = None
        icon = "emblem-music-symbolic"

        if video_id:
            route = "song"
            artist = item.get("artist", "")
            subtitle = artist or item.get("album", "")
            icon = "audio-x-generic-symbolic"
        elif playlist_id:
            route = "playlist"
            subtitle = item.get("description") or item.get("count", "")
            icon = "view-list-symbolic"
        elif browse_id and (
            result_type == "album" or browse_id.startswith(("MPRE", "MPLA"))
        ):
            route = "album"
            subtitle = item.get("year") or "Album"
            icon = "media-optical-symbolic"
        elif browse_id and (
            result_type == "artist" or browse_id.startswith("UC")
        ):
            route = "artist"
            subtitle = item.get("subscribers") or "Artist"
            icon = "avatar-default-symbolic"
        else:
            return None

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.add_css_class("card")
        card.add_css_class("recommendation-card")

        artwork_button = Gtk.Button()
        artwork_button.add_css_class("recommendation-card-main")
        artwork_button.set_tooltip_text(
            "Play song" if route == "song" else f"Open {route}")
        artwork_button.connect(
            "clicked", lambda *_: self._open_recommendation(route, item))

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        artwork = Gtk.Overlay()
        artwork.set_size_request(220, 124)
        picture = Gtk.Picture()
        picture.set_content_fit(Gtk.ContentFit.COVER)
        picture.set_can_shrink(True)
        picture.set_hexpand(True)
        picture.set_vexpand(True)
        picture.set_size_request(220, 124)
        picture.add_css_class("recommendation-art")
        artwork.set_child(picture)

        placeholder = Gtk.Image.new_from_icon_name(icon)
        placeholder.set_pixel_size(40)
        placeholder.set_halign(Gtk.Align.CENTER)
        placeholder.set_valign(Gtk.Align.CENTER)
        placeholder.add_css_class("recommendation-art-placeholder")
        artwork.add_overlay(placeholder)

        url = thumbnail_url(item)
        if url:
            def _set_artwork(texture):
                if texture:
                    picture.set_paintable(texture)
                    placeholder.set_visible(False)

            load_picture_async(url, _set_artwork)

        if route == "song":
            play_overlay = Gtk.Image.new_from_icon_name(
                "media-playback-start-symbolic")
            play_overlay.add_css_class("recommendation-play-overlay")
            play_overlay.set_halign(Gtk.Align.CENTER)
            play_overlay.set_valign(Gtk.Align.CENTER)
            artwork.add_overlay(play_overlay)
        content.append(artwork)

        text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        text.set_margin_start(10)
        text.set_margin_end(10)
        label = Gtk.Label(label=title)
        label.set_halign(Gtk.Align.START)
        label.set_ellipsize(3)
        label.set_max_width_chars(26)
        label.add_css_class("heading")
        text.append(label)

        if subtitle:
            description = Gtk.Label(label=str(subtitle))
            description.set_halign(Gtk.Align.START)
            description.set_ellipsize(3)
            description.set_max_width_chars(26)
            description.add_css_class("caption")
            description.add_css_class("dim-label")
            text.append(description)
        content.append(text)
        artwork_button.set_child(content)
        card.append(artwork_button)

        if route == "song":
            actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            actions.set_halign(Gtk.Align.END)
            actions.set_margin_end(6)
            if self.on_queue:
                queue_button = Gtk.Button()
                queue_button.set_icon_name("list-add-symbolic")
                queue_button.set_tooltip_text("Add to queue")
                queue_button.add_css_class("flat")
                queue_button.add_css_class("circular")
                queue_button.connect("clicked", lambda *_: self.on_queue(item))
                actions.append(queue_button)
            if self.on_download:
                download_button = Gtk.Button()
                download_button.set_icon_name("folder-download-symbolic")
                download_button.set_tooltip_text("Download")
                download_button.add_css_class("flat")
                download_button.add_css_class("circular")
                download_button.connect(
                    "clicked", lambda *_: self.on_download(item))
                actions.append(download_button)
            if actions.get_first_child():
                card.append(actions)

        flow_child = Gtk.FlowBoxChild()
        flow_child.set_child(card)
        return flow_child

    def _open_recommendation(self, route: str, item: dict):
        if route == "song":
            self.on_play(item)
            return

        self._load_id += 1
        load_id = self._load_id
        self._show_spinner()

        def _fetch():
            try:
                if route == "playlist":
                    tracks = self.api.get_playlist_tracks(item["playlistId"])
                elif route == "album":
                    tracks = self.api.get_album_tracks(item["browseId"])
                else:
                    tracks = self.api.search(
                        item.get("title", ""), filter_="songs", limit=20)
                GLib.idle_add(
                    self._show_tracks, tracks, item.get("title", route), load_id)
            except Exception as exc:
                logger.exception("Could not open recommended %s", route)
                GLib.idle_add(self._show_error, str(exc), load_id)

        threading.Thread(target=_fetch, daemon=True).start()

    def _show_tracks(self, tracks: list[dict], title: str, load_id: int):
        if load_id != self._load_id:
            return
        self._clear_content()
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.set_margin_top(10)
        header.set_margin_bottom(8)
        header.set_margin_start(16)
        header.set_margin_end(16)

        back = Gtk.Button()
        back.set_icon_name("go-previous-symbolic")
        back.set_tooltip_text("Back to recommendations")
        back.add_css_class("flat")
        back.add_css_class("circular")
        back.connect("clicked", lambda *_: self.refresh())
        header.append(back)

        heading = Gtk.Label(label=title)
        heading.add_css_class("title-3")
        heading.set_halign(Gtk.Align.START)
        heading.set_hexpand(True)
        header.append(heading)

        playable = [track for track in tracks if track.get("videoId")]
        if playable and self.on_play_all:
            play_all = Gtk.Button(label="Play All")
            play_all.add_css_class("suggested-action")
            play_all.add_css_class("pill")
            play_all.connect("clicked", lambda *_: self.on_play_all(playable))
            header.append(play_all)

        self._content.append(header)
        if not tracks:
            self._show_status(
                "No tracks found",
                f"YouTube Music returned no tracks for {title}.",
                "emblem-music-symbolic",
            )
            return
        self._content.append(Gtk.Separator(
            orientation=Gtk.Orientation.HORIZONTAL))
        self._content.append(make_track_list(
            tracks,
            on_activate=self.on_play,
            on_queue=self.on_queue,
            on_download=self.on_download,
        ))

    def _show_error(self, message: str, load_id: int):
        if load_id != self._load_id:
            return
        self._show_status(
            "Could not load recommendations",
            message,
            "dialog-error-symbolic",
        )
