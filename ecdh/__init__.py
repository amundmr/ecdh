# -*- coding: utf-8 -*-
"""If fastdiff is imported as a module, then this file will be ran"""

#print("Damn, you just imported ecdh as a module! That is not a supported function yet.")

def get_GC(filepath, am_mass = None, specific_cycles = None):
    import ecdh.cell as cell
    cellobj = cell.Cell(filepath, am_mass, specific_cycles)
    cellobj.get_data()
    cellobj.edit_GC()
    
    return cellobj.GCdata