# MCDC-TNT
Monte Carlo Deterministic Code - Transient Neutronics Testbed


## Quick Set-Up
1. From a terminal with conda installed set up a conda enviroment with `conda create -n mcdc_tnt numba matplotlib pyyaml pytest` which will install all package dependecies for the Numba and Pure Python implementations
2. run `conda activate mcdc_tnt`
3. Clone this github 
4. Run `pip install --user -e .` in project directory to install mcdc_tnt as a local package.
5. Run unit test suite for pure Python and Numba kernels by moving to `tests/` directory and running `pytest` (note that unit test coverage will read as very small as test suites for both implementaitons of pykokkos and pyomp have been removed but the kernels are still there)
6. Run an integration test suite with validation by moving to to `integration/` and running `python test_hardaware.py`. This could take a while as a pure Python implementaion is slow
7. To interface with pacakge directly from command line navigate to package directory `mcdc_tnt/` and run `python run.py -i tc_1.yaml -o output.out -t nb_cpu` to run a test problem using the numba protocols. Can also be ran with `-t pp` for pure python implimentations

## Grading Notes:
1. **Installation:** This package only currently installs using local source files. It's requirements for Numba CPU functionality are Numba, Numpy, Matplotlib, and Pyyaml. Note that due to Numba and Pyomp conflicting Pyomp is not interfaceable in this program without changing the __init__ file in `numba/cpu`.
2. **Documentation:** A sphinx cite is linked in this git hub
3. **Testing:** I do not expect anyone to go through the laborious task of setting up a pykokkos implementation to grade this work. As such I have removed the test files for it so that. This coupled with a lack of tests for the Numba GPU implementation makes my test coverage abysmal. Please take this into consideration and that the numba CPU kernels and pure python kernels have decent test coverage
4. **Examples:** An example test suite is listed to provide the same test case working across multiple pieces of hardware
5. **License:** Is included in this directory
6. **Interface:** Runs with the commands provided in this README

# Installation of PyKokkos
While most machines should be able to operate with the OpenMP backend currently on the Lassen Machine can get the CUDA version. To switch to the OpenMP only version change  `-DENABLE_CUDA` from `ON` to `OFF.

1. `git clone` [`pykokkos-base`](https://github.com/kokkos/pykokkos-base) and the develop granch of [`pykokkos`](github.com/kokkos/pykokkos). To do this in the pykokkos directory run `git fetch` then `git checkout develop`
2. Prep conda environment by snagging requirements listed in requirements.txt from pykokkos-base and pykokkos. (1. `conda create -n pyk` 2. `conda activate pyk` 3. in pyk-base directory run `conda install --file requirments.txt` 4. in pykokkos directory run `conda install --file requirments.txt`) *ensure that cmake is of version 18 or higher and that gcc/g++ versions are at least 9*
3. Install Pykokkos-base for both OpenMP, and CUDA implementations by running:
`python setup.py install -- -DCMAKE_CXX_COMPILER=g++ -DENABLE_LAYOUTS=ON -DENABLE_MEMORY_TRAITS=OFF -DENABLE_VIEW_RANKS=3 -DENABLE_CUDA=ON -DENABLE_THREADS=OFF -DENABLE_OPENMP=ON -G "Unix Makefiles" -- -j 4` *this will take upwards of 2 hours to build and will consume a considerable ammount of RAM*
4. Install pykokkos using `pip install --user -e .`
5. Run!

## Interface
This project is designed to be interfaced with via the command line and an input.yaml file. An example is listed here:

```
name: 'fissioning_slab'   #name of the simluation (any string)
number of particles: 1e5  #number of particles top initiate in the 
rng seed: 777             #random number seed (int)
particle speed: 1         #particle speed (float)
neutrons per fission: 2   #how many neutrons to produce per fission event
isotropic: Ture           #isotropic source? if true than particles produced with a random direction

length of slab: 1         #width of the slab
surface locations: [0,1]  #region geometry deffitinition (vector of floats)

dx: 0.01   #mesh width (for error and scalar flux tracking) (float)

hardware target: nb_cpu          #specifying the hardware target: pp/nb_cpu/nb_gpu/pyk_cpu/pyk_gpu
print warmup times: True         #print warm up times

assemble mesh: True             #assemble mesh from crossections listed here
capture cross section: 0.333    #should be as many values here as regions specified in surface_locations
scatter cross section: 0.333
fission cross section: 0.333

file output: True      #should it output flux and stats? if a special file name is desiered supple in command line

error plot: True       #produce the error plot?
flux plot: True        #produce the flux plot?
```

Then to run a simulation it can be done from a python file using:
```
import mcdc_tnt
mcdc_tnt.run('input.yaml','output.out','hardware_target')
```

or from the command line in the mcdc_tnt directory with:
`python run.py -i input.yaml -o output.out -t 'hardware_target'`


## Acknowledgment
This work was supported by the Center for Exascale Monte-Carlo Neutron Transport (CEMeNT) a PSAAP-III project funded by the Department of Energy, grant number: DE-NA003967.
