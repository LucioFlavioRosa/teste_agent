class DIContainer:
    def __init__(self):
        self.providers = {}
    def register(self, interface, implementation):
        self.providers[interface] = implementation
    def resolve(self, interface):
        impl = self.providers.get(interface)
        if impl:
            return impl
        raise Exception(f'Provider for {interface} not registered')
