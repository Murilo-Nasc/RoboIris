from setuptools import find_packages, setup

package_name = 'face_detector'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='robofei',
    maintainer_email='160672626+jaogui@users.noreply.github.com',
    description='Face detector',
    license='Apache 2.0',
    #tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        	'face_detector = face_detector.face_detector_node:main',
        ],
    },
)
