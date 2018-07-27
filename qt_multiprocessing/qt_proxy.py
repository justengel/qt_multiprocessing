import mp_event_loop


__all__ = ['WidgetProxy']


class WidgetProxy(mp_event_loop.Proxy):
    """Proxy to create a widget in a separate process."""

    PROXY_CLASS = None
    SHOW_WIDGET = True

    def create_mp_object(self, *args, **kwargs):
        obj = self.PROXY_CLASS(*args, **kwargs)
        if self.SHOW_WIDGET:
            try:
                obj.show()
            except AttributeError:
                pass
        return obj
