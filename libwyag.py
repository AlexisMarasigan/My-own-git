import argparse #This is for making CLI commands
import collections #We'll need OrderedDict from this one
import configparser #This helps us to build a structure similar to Microsoft Windows INI files
from datetime import datetime
import grp , pwd 
from fnmatch import fnmatch #This helps us support .gitignore 
import hashlib #This provides us the SHA-1 function
from math import ceil 
import os 
import re
import sys
import zlib

argparser = argparse.ArgumentParser(description = "My own version control")
argsubparser = argparse.add_subparsers(title = "Commands",dest = "command") #subcommands
argsubparser.required = True #with these we require the subcommand during use

#Bridge functions
def main(argv=sys.argv[1:]):
    args = argparser.parse_args(argv)
    match args.command:
        case "add"          : cmd_add(args)
        case "cat-file"     : cmd_cat_file(args)
        case "check-ignore" : cmd_check_ignore(args)
        case "checkout"     : cmd_checkout(args)
        case "commit"       : cmd_commit(args)
        case "hash-object"  : cmd_hash_object(args)
        case "init"         : cmd_init(args)
        case "log"          : cmd_log(args)
        case "ls-files"     : cmd_ls_files(args)
        case "ls-tree"      : cmd_ls_tree(args)
        case "rev-parse"    : cmd_rev_parse(args)
        case "rm"           : cmd_rm(args)
        case "show-ref"     : cmd_show_ref(args)
        case "status"       : cmd_status(args)
        case "tag"          : cmd_tag(args)
        case _              : print("Bad command.")


#GitRepository class
class GitRepository (object):
    """A git repository"""
    worktree = None
    gitdir = None
    conf = None

    #Repo Constructor
    def __init__(self, path, force=False):
        self.worktree = path
        self.gitdir = os.path.join(path, ".git")

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception("Not a Git repository %s" % path)
        
        #Read configuration file in .git/config
        self.conf = configparser.ConfigParser()
        cf = self.repo_file(self, "config")

        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise Exception("configuration file missing")
        
        if not force:
            vers = int(self.conf.get("core", "repositoryformatversion"))
            if vers != 0:
                raise Exception("Unsupported repositoryformatversion %s" % vers)
            
    
    def repo_path(self, repo, *path):
        """Compute path under repo's gitdir."""
        return os.path.join(repo.gitdir, *path)
    
    def repo_file(self, *path, mkdir=False):
        """Same as repo_path, but create dirname(*path) if absent."""
        if self.repo_dir(*path[:-1], mkdir=mkdir):
            return self.repo_path(*path)
        
    def repo_dir(self, repo, *path, mkdir = False):
        """Same as repo_path, but mkdir *path if absent mkdir"""

        path = self.repo_path(repo, *path)

        if os.path.exists(path):
            if (os.path.isdir(path)):
                return path
            else:
                raise Exception("Not a directory %s" % path)
            
        if mkdir:
            os.makedirs(path)
            return path
        else:
            return None
        
    def repo_create(self,path):
        """Create a new repository at path"""
        
        repo = GitRepository(path, True)

        # First, we make sure the path either doesn't exist or is an
        # empty dir.

        if os.path.exists(repo.worktree):
            if not os.path.isdir(repo.worktree):
                raise Exception ("%s is not a directory!" % path)
            if os.path.exists(repo.gitdir):
                raise Exception ("%s is not empty!" % path)
        else:
            os.makedirs(repo.worktree)
        
        assert self.repo_dir(repo, "branches", mkdir=True)
        assert self.repo_dir(repo, "objects", mkdir=True)
        assert self.repo_dir(repo, "refs", "tags", mkdir=True)
        assert self.repo_dir(repo, "refs", "heads", mkdir=True)

        # .git/description
        with open(self.repo_file(repo, "description"), "w") as f:
            f.write("Unnamed repository; edit this file 'description' to name the repository.\n")

    # .git/HEAD
        with open(self.repo_file(repo, "HEAD"), "w") as f:
            f.write("ref: refs/heads/master\n")

        with open(self.repo_file(repo, "config"), "w") as f:
            config = self.repo_default_config()
            config.write(f)

        return repo
        