from setuptools import setup

setup(
    name='httpybench',
    version='1.0',
    packages=[''],
    url='https://github.com/h593267/HttPyBench',
    license='MIT',
    author='Arne Giacomo Munthe-Kaas',
    author_email='arnegiacomo@gmail.com',
    description='A simple yet customisable CLI-based python script to benchmark cURL commands to your web applications.',
    install_requires=open('requirements.txt').readlines()
)
