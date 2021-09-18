import glob
import pstats
from pstats import SortKey
from os import listdir
from os.path import join as join_path
from os.path import basename
from os.path import isfile, join
from IPython.display import display, Markdown
import mathics


threshold = 100
branch = "singletonize"


# Check if ipython is available

ipython = True
try:
    get_ipython()
except:
    ipython = False

if ipython:

    def show_table(t):
        display(Markdown(t))


else:

    def show_table(t):
        print(t)


profiles_directory = mathics.__path__[0][:-8]
stats = dict()

# Load the stored profiles
for sf in [
    f
    for f in glob.glob(join_path(profiles_directory, "profiles", "*.pstats"))
    if isfile(f)
]:
    key = basename(sf).split(".")[0]
    stats[key] = pstats.Stats(sf)


def show_comparison(key1, key2):
    sp1 = stats[key1].stats
    sp2 = stats[key2].stats
    funcidxs = [k for k in sp1.keys() if k in sp2.keys()]
    data = [[" ".join([str(c) for c in k]), sp1[k], sp2[k]] for k in funcidxs]
    data = [
        [
            (d[2][1]),
            float(100 * (1 - d[2][1] / d[1][1])),
            (float(d[2][2])),
            (float(100 * (1 - d[2][2] / d[1][2]))),
            (float(d[2][3])),
            (float(100 * (1 - d[2][3] / d[1][3]))),
            d[0],
        ]
        for d in data
        if "docpipeline" not in d[0]
    ]

    data = [d for d in data if (d[5] < -1)]
    data = [d for d in data if ("/mathics-core/" in d[6])]
    data = [d[:-1] + [d[-1][45:]] for d in data]
    show_table(build_comparison_table(sorted(data, key=lambda x: -x[0])[:100]))


def build_comparison_table(data, key=0, invert=False):
    mdtable = ""
    mdtable = "|\tncals\t\t|\ttotal\t\t|\tcumulative\t|\t\t\tfunc\t\t\t|\n"
    mdtable += (
        "|:" + 21 * "-" + ":|:" + 21 * "-" + ":|:" + 21 * "-" + ":|:" + 46 * "-" + "|\n"
    )
    fmt = "|%1.2e (%2.0f o/o)\t|%8.3f (%2.0f o/o)\t|%8.3f(%2.0f o/o)\t|%s\t|\n"
    if invert:
        for d in sorted(data, key=lambda x: x[key]):
            mdtable += fmt % tuple(d)
    else:
        for d in sorted(data, key=lambda x: -x[key]):
            mdtable += fmt % tuple(d)
    show_table(mdtable)


def show_speedups_and_slowdowns(key1, key2, threshold=20):
    sp1 = stats[key1].stats
    sp2 = stats[key2].stats
    funcidxs = [k for k in sp1.keys() if k in sp2.keys()]
    data = [[" ".join([str(c) for c in k]), sp1[k], sp2[k]] for k in funcidxs]
    data = [
        [
            (d[2][1]),
            float(100 * (1 - d[2][1] / d[1][1])),
            (float(d[2][2])),
            (float(100 * (1 - d[2][2] / d[1][2]))),
            (float(d[2][3])),
            (float(100 * (1 - d[2][3] / d[1][3]))),
            d[0],
        ]
        for d in data
        if "docpipeline" not in d[0]
    ]
    data = [d for d in data if ("/mathics-core/" in d[6])]
    data = [d[:-1] + [d[-1][45:]] for d in data]
    show_table("## Performance improvements")
    data_improve_calls = [d for d in data if d[1] >= threshold]
    show_table("### reduce numbers of calls")
    if data_improve_calls:
        show_table(build_comparison_table(data_improve_calls, 0))
    else:
        show_table("\tNone over the threshold")

    data_improve_calls = [d for d in data if d[5] >= threshold]
    show_table("### reduce cumulative time")
    if data_improve_calls:
        show_table(build_comparison_table(data_improve_calls, 4))
    else:
        show_table("\tNone over the threshold")

    show_table("\n\n## Performance slowdown")
    data_improve_calls = [d for d in data if d[1] <= -threshold]
    show_table("### increase in number of calls")
    if data_improve_calls:
        show_table(build_comparison_table(data_improve_calls, 0))
    else:
        show_table("\tNone over the threshold")

    data_improve_calls = [d for d in data if d[5] <= -threshold]
    show_table("## increase in cumulative time")
    if data_improve_calls:
        show_table(build_comparison_table(data_improve_calls, 4))
    else:
        show_table("\tNone over the threshold")


show_table(80 * "-")
show_table("\n\n")
show_table(f"# Profile comparison between {branch} and master")

show_speedups_and_slowdowns("master", branch, threshold=threshold)
