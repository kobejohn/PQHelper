try:
    from setuptools import setup
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup


setup(
    name='PQHelper',
    version='0.1.0',
    py_modules=['distribute_setup'],
    packages=['pqhelper'],
    requires=['numpy', 'treenode', 'investigators'],
    tests_require=['mock', 'numpy', 'treenode', 'investigators'],
    include_package_data=True,
    url='http://github.com/kobejohn/PQHelper',
    license='MIT',
    author='KobeJohn',
    author_email='niericentral@gmail.com',
    description='Analyze, and advise on the game called Puzzle Quest.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Programming Language :: Python :: 2.7']
)
