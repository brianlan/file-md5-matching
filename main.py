import shutil
import argparse
import pathlib
import subprocess
import platform

parser = argparse.ArgumentParser(description='Find the matching between folders of files.')
parser.add_argument('--dir-queries', required=True, help='Dir of the files to be queried about.')
parser.add_argument('--dir-file-pool', required=True, help='Dir of all the entire files.')
parser.add_argument('--result-save-path', required=True)
parser.add_argument('--suffix')


def get_md5sum_stdout(dir_path, suffix):
    exec_str = 'find %s -name "*.%s" | xargs md5sum' % (dir_path, suffix)
    p = subprocess.Popen(exec_str, stdout=subprocess.PIPE, shell=True)
    return p.communicate()


def calc_md5_for_dir(dir_path, suffix):
    output, err = get_md5sum_stdout(dir_path, suffix)
    lines = [line.split() for line in output.strip().split(b'\n')]
    return {line[0].decode(): line[1].decode() for line in lines}


def write_results(results, save_path):
    pathlib.Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, 'w') as f:
        for query_path, matching_path in results.items():
            f.write('{},{}\n'.format(query_path, matching_path or ''))


def calc_match_results(queries, file_pool):
    return {path: file_pool.get(md5) for md5, path in queries.items()}


def check_platform_support():
    if platform.system().lower() == 'windows':
        print('Sorry, this tool is not supported on Windows platform yet.')
        exit(-1)


def check_md5sum_exists():
    if shutil.which('md5sum') is None:
        print('Sorry, this tool depends on md5sum but can not be found.')
        exit(-1)


def main(args):
    check_platform_support()
    check_md5sum_exists()
    queries = calc_md5_for_dir(args.dir_queries, args.suffix)
    file_pool = calc_md5_for_dir(args.dir_file_pool, args.suffix)
    results = calc_match_results(queries, file_pool)
    write_results(results, args.result_save_path)


if __name__ == '__main__':
    main(parser.parse_args())
