import sys
import argparse
from quinteract import Quinteract

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--infile', action='store', required=True)
    parser.add_argument('--outfile', action='store')
    parser.add_argument('--rows', action='store', type=int, default=5)
    parser.add_argument('--cols', action='store', type=int, default=5)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--text', action='store_true')
    group.add_argument('--overlay', action='store_true')
    group.add_argument('--grid', action='store_true')

    args = parser.parse_args()

    q = Quinteract(args.infile)

    if args.outfile:
        if args.text:
            with open(outfile, 'wb') as out:
                out.write(q.text)
        elif args.overlay:
            q.generate_text_overlay(filename=args.outfile)
        elif args.grid:
            q.generate_grid_overlay(filename=args.outfile, rows=args.rows, cols=args.cols)

    else:
        if args.text:
            print q.text
        elif args.overlay:
            print q.generate_text_overlay()
        elif args.grid:
            print q.generate_grid_overlay(rows=args.rows, cols=args.cols)

if __name__ == '__main__':
    main()
