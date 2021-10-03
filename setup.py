from setuptools import setup

setup(
        name="nicole",
        version="1.1",
        description="Add lyrics from azlyrics.com to mp3-tag",

        author="Matthias Quintern",
        author_email="matthiasqui@protonmail.com",

        url="https://github.com/MatthiasQuintern/nicole.git",

        license="GPLv3",

        packages=["nicole"],
        install_requires=["mutagen"],

        classifiers=[
            "Operating System :: POSIX :: Linux",
            "Environment :: Console",
            "Programming Language :: Python :: 3",
            "Topic :: Multimedia :: Audio",
            "Topic :: Utilities",
            ],

        # scripts=["bin/nicole"],
        entry_points={
            "console_scripts": [ "nicole=nicole.nicole:main" ],
            },
)


