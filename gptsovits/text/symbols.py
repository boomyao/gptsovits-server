from .constants import PAD, C_SYMBOLS, V_SYMBOLS, JA_SYMBOLS, PU_SYMBOLS, ARPA_SYMBOLS, KO_SYMBOLS, YUE_SYMBOLS

def generate_symbols():
    # Combine all symbols into one list and sort
    symbols = [PAD] + C_SYMBOLS + V_SYMBOLS + JA_SYMBOLS + PU_SYMBOLS + list(ARPA_SYMBOLS)
    symbols = sorted(set(symbols))
    
    # Add additional symbols
    symbols += ["[", "]"]  # Japanese pitch accents
    symbols += sorted(list(KO_SYMBOLS))
    symbols += sorted(list(YUE_SYMBOLS))
    
    return symbols


def get_symbols():
    if not hasattr(get_symbols, "symbols"):
        get_symbols.symbols = generate_symbols()
    return get_symbols.symbols