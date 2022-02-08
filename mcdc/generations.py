#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: Testbed_1
breif: Event Based Transient MC for metaprograming exploration
Author: Jackson Morgan (OR State Univ - morgjack@oregonstate.edu) CEMeNT
Date: Dec 2nd 2021
current implemented physics:
        -slab geometry
        -multiregion
        -surface tracking
        -track length estimator
        -monoenergtic
        -isotropic or uniform source direction
        -fission/capture/scatter region
        -purging the dead
"""
# import sys
# sys.path.append('/home/jack/Documents/testbed/serial/kernals/')
import numpy as np


import kernels.SourceParticles
import kernels.Advance
import kernels.SampleEvent
import kernels.FissionsAdd
import kernels.CleanUp
import kernels.Scatter


#===============================================================================
# Simulation Setup
#===============================================================================



#===============================================================================
# EVENT 0 : Sample particle sources
#===============================================================================

def Generations(seed, num_part, particle_speed, nu_new_neutrons, isotropic, mesh_cap_xsec, mesh_scat_xsec, mesh_fis_xsec, mesh_total_xsec, L, N_mesh, dx, surface_distances):
    
    
    #===============================================================================
    # Initial setups
    #===============================================================================
    
    # Initialize RNG
    np.random.seed(seed)
    
    init_particle = num_part
    meshwise_fission_pdf = np.zeros(N_mesh, dtype=np.float32)
    
    total_mesh_fission_xsec = sum(mesh_fis_xsec)
    for cell in range(N_mesh):
        meshwise_fission_pdf[cell] = mesh_fis_xsec[cell]/total_mesh_fission_xsec
        
        mesh_cap_xsec[cell] = mesh_cap_xsec[cell] / mesh_total_xsec[cell]
        mesh_scat_xsec[cell] = mesh_scat_xsec[cell] / mesh_total_xsec[cell]
        mesh_fis_xsec[cell] = mesh_fis_xsec[cell] / mesh_total_xsec[cell]
        
    meshwise_fission_pdf /= sum(meshwise_fission_pdf)
    mesh_dist_traveled = np.zeros(N_mesh, dtype=np.float32)
    mesh_dist_traveled_squared = np.zeros(N_mesh, dtype=np.float32)
    
    
    #===============================================================================
    # Allocate particle phase space
    #===============================================================================
    
    phase_parts = 5*num_part #see note about data storage
    
    # Position
    p_pos_x = np.zeros(phase_parts, dtype=np.float32)
    p_pos_y = np.zeros(phase_parts, dtype=np.float32)
    p_pos_z = np.zeros(phase_parts, dtype=np.float32)
    
    # Direction
    p_dir_x = np.zeros(phase_parts, dtype=np.float32)
    p_dir_y = np.zeros(phase_parts, dtype=np.float32)
    p_dir_z = np.zeros(phase_parts, dtype=np.float32)
    
    # Speed
    p_speed = np.zeros(phase_parts, dtype=np.float32)
    
    # Time
    p_time = np.zeros(phase_parts, dtype=np.float32)
    
    # Region
    p_mesh_cell = np.zeros(phase_parts, dtype=int)
    
    # Flags
    p_alive = np.full(phase_parts, False, dtype=bool)
    p_event = np.zeros(phase_parts, dtype=np.uint8)
    
    #mesh_particle_index = np.zeros([N_mesh, phase_parts], dtype=np.uint8)
    
    
    scatter_event_index = np.zeros(phase_parts, dtype=np.uint8)
    capture_event_index = np.zeros(phase_parts, dtype=np.uint8)
    fission_event_index = np.zeros(phase_parts, dtype=np.uint8)
    
    
    [p_pos_x, p_pos_y, p_pos_z, p_mesh_cell, p_dir_y, p_dir_z, p_dir_x, p_speed, p_time, 
    p_alive] = kernals.SourceParticles.SourceParticles(p_pos_x, p_pos_y,
                                                      p_pos_z, p_mesh_cell, dx,
                                                      p_dir_y, p_dir_z, p_dir_x,
                                                      p_speed, p_time, p_alive,
                                                      num_part, meshwise_fission_pdf,
                                                      particle_speed, isotropic)
    
    #===============================================================================
    # Generation Loop
    #===============================================================================
    trans = 0
    g = 0
    alive = num_part
    trans_lhs = 0
    trans_rhs = 0
    while alive > 0:
        print("")
        print("===============================================================================")
        print("                             Event Cycle {0}".format(g))
        print("===============================================================================")
        print("particles alive at start of event cycle {0}".format(num_part))
        
        # print("max index {0}".format(num_part))
        #===============================================================================
        # EVENT 1 : Advance
        #===============================================================================
        killed = 0
        alive_cycle_start = num_part
        
        
        [p_pos_x, p_pos_y, p_pos_z, p_mesh_cell, p_dir_y, p_dir_z, p_dir_x, p_speed, p_time, mesh_dist_traveled, mesh_dist_traveled_squared] = kernals.Advance.Advance(
                p_pos_x, p_pos_y, p_pos_z, p_mesh_cell, dx, p_dir_y, p_dir_z, p_dir_x, p_speed, p_time,
                num_part, mesh_total_xsec, mesh_dist_traveled, mesh_dist_traveled_squared, surface_distances[len(surface_distances)-1])
        
        #===============================================================================
        # EVENT 2 : Still in problem
        #===============================================================================
        [p_alive, tally_left_t, tally_right_t] = kernals.Advance.StillIn(p_pos_x, surface_distances, p_alive, num_part)
        
        trans_lhs += tally_left_t
        trans_rhs += tally_right_t
        
        #===============================================================================
        # EVENT 3 : Sample event
        #===============================================================================
        
        [scatter_event_index, scat_count, capture_event_index, cap_count, fission_event_index, fis_count] = kernals.SampleEvent.SampleEvent(
                p_mesh_cell, p_event, p_alive, mesh_cap_xsec, mesh_scat_xsec, mesh_fis_xsec, scatter_event_index,
                capture_event_index, fission_event_index, num_part, nu_new_neutrons)
        
        fissions_to_add = (fis_count)*nu_new_neutrons
        
        killed += cap_count+fis_count
        
        
        #===============================================================================
        # EVENT 3 : Scatter
        #===============================================================================
        
        [p_dir_x, p_dir_y, p_dir_z] = kernals.Scatter.Scatter(scatter_event_index, scat_count, p_dir_x, p_dir_y, p_dir_z)
        
        
        #===============================================================================
        # EVENT 4: Generate fission particles
        #===============================================================================
        # print("")
        # print("max index {0}".format(num_part))
        # print("")
        
        [p_pos_x, p_pos_y, p_pos_z, p_mesh_cell, p_dir_y, p_dir_z, p_dir_x, p_speed, 
         p_time, p_alive, particles_added_fission] = kernals.FissionsAdd.FissionsAdd(p_pos_x, p_pos_y, p_pos_z, p_mesh_cell, 
                                                  p_dir_y, p_dir_z, p_dir_x, p_speed, 
                                                  p_time, p_alive, fis_count, nu_new_neutrons, 
                                                  fission_event_index, num_part, particle_speed)
    
        num_part += particles_added_fission
        # print("")
        # print("max index {0}".format(num_part))
                                                  
        #===============================================================================
        # Criticality & Output (not really an event)
        #===============================================================================
        
        # criticality = fissions_to_add/killed
        # print("k = {0} (birth/death)".format(criticality))
                
        # alive_now =0
        # for i in range(num_part):
        #     if p_alive[i] == True:
        #         alive_now +=1
        # print("k = {0} (pop now/pop last)".format(alive_now/alive_last))
        
            
        #===============================================================================
        # Event 5: Purge the dead
        #===============================================================================
        
        [p_pos_x, p_pos_y, p_pos_z, p_mesh_cell, p_dir_y, p_dir_z, p_dir_x, p_speed, 
         p_time, p_alive, kept] = kernals.CleanUp.BringOutYourDead(p_pos_x, p_pos_y, p_pos_z, p_mesh_cell, 
                                                   p_dir_y, p_dir_z, p_dir_x, p_speed, 
                                                   p_time, p_alive, p_event, num_part)
                                                   
        num_part = kept
        alive = num_part
                          
        # print("max index {0}".format(num_part))
        # print("")
        
        # print(max(p_mesh_cell[0:num_part]))
    
    #===============================================================================
    # Step Output
    #===============================================================================
    
    
    mesh_dist_traveled /= init_particle
    mesh_dist_traveled_squared /= init_particle
    standard_deviation_flux = ((mesh_dist_traveled_squared - mesh_dist_traveled**2)/(init_particle-1))
    standard_deviation_flux = np.sqrt(standard_deviation_flux/(init_particle))
    
    x_mesh = np.linspace(0,surface_distances[len(surface_distances)-1], N_mesh)
    scalar_flux = mesh_dist_traveled/dx
    scalar_flux/=max(scalar_flux)
    
    return(scalar_flux, standard_deviation_flux)
    
    # # the sum of all debits from functional operations should be the number of
    # #currently alive particles
    # account = alive_cycle_start + particles_added_fission - fis_count - cap_count - tally_left_t - tally_right_t
    # if account != num_part:
    #     print("ERROR PARTICLES HAVE BEEN UNACCOUNTED FOR")
    
    # print("{0} particles are produced from {1} fission events".format(fissions_to_add, fis_count))
    # print("particles captured:  {0}".format(cap_count))
    # print("particles scattered: {0}".format(scat_count))
    # print("particles leaving left:    {0}".format(tally_left_t))
    # print("particles leaving right:   {0}".format(tally_right_t))
    # print("total particles now alive and stored: {0}".format(num_part))
    
    # # alive_last = alive_now
    # g+=1




