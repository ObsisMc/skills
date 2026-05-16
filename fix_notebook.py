import nbformat

path = r"E:\Data\GitRepo\skills\kaggle\eda\playground-s6e5-f1-pitstops-eda-20260515-2143\eda.ipynb"
nb = nbformat.read(path, as_version=4)

# 添加 kernelspec
nb["metadata"]["kernelspec"] = {
    "name": "python3",
    "display_name": "Python 3",
    "language": "python",
}

nbformat.write(nb, path)
