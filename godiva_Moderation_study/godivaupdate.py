import openmc
import numpy as np
import os
import math

def Run_System(R_index=3,THERMAL=False):
    if THERMAL: Save_to_Txt = open('Thermal_Data.txt','a+t')
    else: Save_to_Txt = open('Fast_Data.txt','a+t')

    # Material Composition of the Godiva Sphere
    R_Array = np.array([50,100,150,200,250,300,350])
    R = R_Array[R_index]
    fuel = openmc.Material(name="Fuel",material_id=1)
    fuel.set_density('g/cm3', 18.7398)
    fuel.add_element('U', 1.0, enrichment=20)
    fuel.add_element('O',R)
    fuel.add_element('H',R*2)
    fuel.add_s_alpha_beta('c_H_in_H2O',1)
    print(fuel.get_mass_density())
    materials = openmc.Materials([fuel])

    # If System is thermal, moderator (Graphite) is added
    if THERMAL:
        mod = openmc.Material(name="Moderator",material_id=2)
        mod.set_density('g/cm3',1.0)
        mod.add_element('H',2.0)
        mod.add_element('O',1.0)
        fuel_mod = openmc.Material.mix_materials([fuel,mod],[1/501,500/501],'ao')
        fuel_mod.add_s_alpha_beta('c_H_in_H2O',1)
        fuel_mod.set_density('g/cm3',fuel.get_mass_density())
        materials = openmc.Materials([fuel_mod])
    else:
        materials = openmc.Materials([fuel])
    materials.export_to_xml()

    # Create geometry
    sphere = openmc.Sphere(r=10.7407, boundary_type='vacuum')
    cell1 = openmc.Cell(fill=fuel, region=-sphere)
    geom = openmc.Geometry([cell1])
    geom.export_to_xml()

    # Begins the data line with radius
    Save_to_Txt.write(f'\n{R}')

    # Create Base Settings of Source and Generations
    settings = openmc.Settings()
    settings.particles = 100000
    n = 200
    settings.batches = n
    settings.inactive = 50

    # Saving Flux Tallies to produce energy spectrum
    e_min, e_max = 1e-5, 20.0e6
    groups = 500
    energies = np.logspace(math.log10(e_min), math.log10(e_max), groups + 1)
    energy_filter = openmc.EnergyFilter(energies)

    spectrum_tally = openmc.Tally(name="Flux spectrum")
    spectrum_tally.filters = [energy_filter]
    spectrum_tally.scores = ['flux']

    tallies = openmc.Tallies([spectrum_tally])
    tallies.export_to_xml()

    for AR in [False,True]:
        settings.alpha_mode = AR
        for PO in [False,True]:
            settings.prompt_only = PO
            settings.export_to_xml()

            if not ((AR == False) and (PO)):
                openmc.run()

                if THERMAL: ft = 'Th'
                else: ft = 'Fa'
                if AR: ak = 'alpha'
                else: ak = 'k_eff'
                if PO: pd = 'prompt'
                else: pd = 'delayed'

                os.rename('statepoint.{}.h5'.format(n),'sp.{}.{}.{}ratio.{}.{}.h5'.format(n,ft,R,ak,pd))
                with openmc.StatePoint('sp.{}.{}.{}ratio.{}.{}.h5'.format(n,ft,R,ak,pd)) as sp_file:
                    if AR: data = sp_file.alpha_eff
                    else: data = sp_file.keff.nominal_value
                    Save_to_Txt.write(f" {data}")

    Save_to_Txt.close()



for i in range(7):
    Run_System(R_index=i)
    

#Run_System(R_index=3,THERMAL=True)
