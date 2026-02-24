def classFactory(iface):
    from .selection_counter import SelectionCounterPlugin
    return SelectionCounterPlugin(iface)
