from setuptools import setup
import json


with open("metadata.json", encoding="utf-8") as fp:
    metadata = json.load(fp)


setup(
    name="lexibank_kpaamcam",
    description=metadata["title"],
    license=metadata.get("license", ""),
    url=metadata.get("url", ""),
    py_modules=["lexibank_kpaamcam"],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "lexibank.dataset": [
            "kpaamcam=lexibank_kpaamcam:Dataset"
        ],
        'cldfbench.commands': [
            'lowerfungom=kpaamcamcommands',
        ],
    },
    install_requires=[
        "pylexibank>=2.6.0", 
        "python-igraph", 
        "matplotlib",
        "scipy",
        "pandas"],
    extras_require={"test": ["pytest-cldf"]},
)
