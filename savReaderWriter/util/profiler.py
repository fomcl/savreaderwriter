#python -m cProfile -o savViewer.prof savViewer.py big.sav
import pstats
p = pstats.Stats('savViewer.prof')
p.sort_stats('cum').print_stats(100)

