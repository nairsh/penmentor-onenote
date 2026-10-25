"""OneNote has no way to hand over the whole page, so the model sees the screen only. PageRequest keeps the callers
(cli, overlay) as they were in the xournal++ original; ponytail: add a Microsoft Graph page export here if scrolled-away
problem statements turn out to matter."""


class PageRequest:
    on = False

    def result(self, wait=1.5):
        return None
