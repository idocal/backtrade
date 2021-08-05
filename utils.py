def env_vars():
    env_filename = '.env'
    ret = {}
    with open(env_filename, 'r') as f:
        for line in f:
            line = line[:-1]  # remove newline
            key, value = line.split('=')
            ret[key] = value
    return ret
