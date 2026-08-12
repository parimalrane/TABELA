import textwrap

def print_row(micro, macro, total, qual, score, state, stocks):
    micro = (micro[:26] + "..") if len(micro) > 28 else micro.ljust(28)
    macro = (macro[:13] + "..") if len(macro) > 15 else macro.ljust(15)
    tot = str(total).rjust(4)
    q = str(qual).rjust(4)
    s = f"{score:>.2f}".rjust(7)
    mac_state = state.ljust(14)
    
    prefix = f"{micro}  {macro}  {tot}  {q}  {s}  {mac_state}  "
    prefix_len = len(prefix)
    
    if not stocks:
        print(prefix)
        return
        
    wrapped = textwrap.wrap(stocks, width=(130 - prefix_len))
    
    for i, line in enumerate(wrapped):
        if i == 0:
            print(f"{prefix}{line}")
        else:
            print(" " * prefix_len + line)
            
print(f"{'Micro Theme'.ljust(28)}  {'Macro Theme'.ljust(15)}  {'Tot'.rjust(4)}  {'Qual'.rjust(4)}  {'Score'.rjust(7)}  {'Macro State'.ljust(14)}  {'Stocks'}")
print("-" * 130)
print_row("Communications Cloud", "Cloud Computing", 3, 3, 128.46, "Leading (#3)", "RNG, TWLO, FIVN, MSFT, ORCL, CRM, ZM")
print_row("Oilfield Chemicals & Data Analytics", "Energy", 1, 1, 68.62, "Neutral (#40)", "FTK")
print_row("Cybersecurity", "Software", 13, 9, 159.76, "Neutral (#8)", "QLYS, OKTA, PANW, CRWD, FTNT, #ATEN, #RPD, DOCN, FSLY, SNOW, NET, DDOG, SPLK")
