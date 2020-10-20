import builtins
import os
import sys
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext

# Skip Cython build if not available
try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None


# Add numpy include dirs without importing numpy on module level.
# derived from scikit-hep:
# https://github.com/scikit-hep/root_numpy/pull/292
class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        # Prevent numpy from thinking it is still in its setup process:
        try:
            del builtins.__NUMPY_SETUP__
        except AttributeError:
            pass

        import numpy

        self.include_dirs.append(numpy.get_include())


ext_modules = []

if "clean" not in sys.argv:
    if not cythonize:
        sys.exit("ERROR: Cython is required to build Cython extensions.")

    cython_modules = [Extension("analysis.lib.speedups", ["analysis/lib/speedups.pyx"])]

    ext_modules += cythonize(
        cython_modules,
        compiler_directives={"language_level": "3"},
        # enable once Cython >= 0.3 is released
        # define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
    )


description = "SECAS Southeast Conservation Blueprint Explorer"

if os.path.exists("README.md"):
    long_description = open("README.md").read()
else:
    long_description = description

setup(
    name="secas-blueprint",
    version="0.1.0",
    url="https://github.com/astutespruce/secas-blueprint",
    license="MIT",
    author="Brendan C. Ward",
    author_email="bcward@astutespruce.com",
    description=description,
    long_description_content_type="text/markdown",
    long_description=long_description,
    cmdclass={"build_ext": build_ext},
    setup_requires=["numpy"],
    install_requires=["numpy>=1.13"],
    python_requires=">=3",
    ext_modules=ext_modules,
)
