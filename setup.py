try:
    from setuptools import setup, find_packages
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


setup(
    name='PQHelper',
    version='0.1.2.3',
    py_modules=['distribute_setup'],
    packages=find_packages(),
    package_data={'': ['*.png']},
    install_requires=['numpy', 'treenode', 'investigators'],
    tests_require=['mock', 'numpy', 'treenode', 'investigators'],
    url='http://github.com/kobejohn/PQHelper',
    license='MIT',
    author='KobeJohn',
    author_email='niericentral@gmail.com',
    description='Get advice on the game called Puzzle Quest.',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Programming Language :: Python :: 2.7']
)
