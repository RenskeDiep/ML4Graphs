class IOHelper:
    value_buffer = []

    @staticmethod
    def store(property_name, v):
        IOHelper.value_buffer.append(f"{property_name} = {v}\n")

    @staticmethod
    def get_params():
        return ''.join(IOHelper.value_buffer)

    @staticmethod
    def get_property(prop, property_name, default_value):
        if property_name in prop:
            v = int(prop[property_name])
            IOHelper.store(property_name, v)
            return v
        else:
            IOHelper.store(property_name, default_value)
            return default_value

    @staticmethod
    def get_property_long(prop, property_name, default_value):
        if property_name in prop:
            v = int(prop[property_name])
            IOHelper.store(property_name, v)
            return v
        else:
            IOHelper.store(property_name, default_value)
            return default_value

    @staticmethod
    def get_property_int_array(prop, property_name, default_values):
        if property_name in prop:
            values = list(map(int, prop[property_name].split(',')))
            values_s = ' '.join(map(str, values))
            IOHelper.store(property_name, values_s)
            return values
        else:
            default_values_s = ' '.join(map(str, default_values))
            IOHelper.store(property_name, default_values_s)
            return default_values

    @staticmethod
    def get_property_double(prop, property_name, default_value):
        if property_name in prop:
            v = float(prop[property_name])
            IOHelper.store(property_name, v)
            return v
        else:
            IOHelper.store(property_name, default_value)
            return default_value

    @staticmethod
    def get_property_boolean(prop, property_name, default_value):
        if property_name in prop:
            v = prop[property_name].lower() in ['true', '1']
            IOHelper.store(property_name, v)
            return v
        else:
            IOHelper.store(property_name, default_value)
            return default_value

    @staticmethod
    def get_property_string(prop, property_name, default_value):
        if property_name in prop:
            v = prop[property_name]
            IOHelper.store(property_name, v)
            return v
        else:
            IOHelper.store(property_name, default_value)
            return default_value

