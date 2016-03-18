from distutils.core import setup
from distutils.core import Extension
MOD = "redes"
module = Extension(MOD, sources=["redes.cpp"],
						extra_link_args=['-std=c++11','-lpqxx','-lpq','-O3','-march=native'])
setup(name = MOD, ext_modules = [module])
