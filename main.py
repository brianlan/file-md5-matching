import shutil
import argparse
import pathlib
import subprocess
import multiprocessing

parser = argparse.ArgumentParser(description='Find the matching between folders of files.')
parser.add_argument('--dir-queries', required=True, help='Dir of the files to be queried about.')
parser.add_argument('--dir-file-pool', required=True, help='Dir of all the entire files.')
parser.add_argument('--result-save-path', required=True)
parser.add_argument('--suffix')
parser.add_argument('--num-processes', default=1, type=int)


def get_file_md5sum(file_path):
    p = subprocess.Popen('md5sum %s' % file_path, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    return output.split()[0].decode()


def get_file_paths(root_dir, suffix):
    p = subprocess.Popen('find %s -name "*.%s"' % (root_dir, suffix), stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    return [line.strip().decode() for line in output.strip().split(b'\n')]


def calc_md5_for_dir(dir_path, suffix, num_processes=1):
    print('Calculating md5 for %s files in %s using %d processes ...' % (suffix, dir_path, num_processes))
    file_paths = get_file_paths(dir_path, suffix)
    with multiprocessing.Pool(processes=num_processes) as pool:
        md5 = pool.map(get_file_md5sum, file_paths)
    return {m: p for m, p in zip(md5, file_paths)}


def write_results(results, save_path):
    pathlib.Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, 'w') as f:
        for query_path, matching_path in results.items():
            f.write('{},{}\n'.format(query_path, matching_path or ''))
    print('Matching results has been saved to %s' % save_path)


def calc_match_results(queries, file_pool):
    print('Calculating matching results between the above directories ...')
    return {path: file_pool.get(md5) for md5, path in queries.items()}


def check_linux_command_exists(commands):
    if any(shutil.which(cmd) is None for cmd in commands):
        print('Sorry, this tool requires commands: {}.'.format(commands))
        exit(-1)
    print('Passed dependency checking for {}'.format(commands))


def main(args):
    check_linux_command_exists(['find', 'xargs', 'md5sum'])
    queries = calc_md5_for_dir(args.dir_queries, args.suffix, num_processes=args.num_processes)
    file_pool = calc_md5_for_dir(args.dir_file_pool, args.suffix, num_processes=args.num_processes)
    results = calc_match_results(queries, file_pool)
    write_results(results, args.result_save_path)


if __name__ == '__main__':
    main(parser.parse_args())
