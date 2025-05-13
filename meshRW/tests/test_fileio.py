import os
import pytest
from pathlib import Path
from meshRW.fileio import fileHandler
import gzip
import bz2

@pytest.fixture
def temp_file(tmp_path):
    """Fixture to create a temporary file for testing."""
    temp_file = tmp_path / "test_file.txt"
    yield temp_file
    if temp_file.exists():
        temp_file.unlink()

def test_fileHandler_initialization(temp_file):
    """Test initialization of fileHandler."""
    handler = fileHandler(filename=temp_file, right='w')
    assert handler.filename == temp_file
    assert handler.right == 'w'
    assert handler.append is False
    handler.close()

def test_fileHandler_write_and_read(temp_file):
    """Test writing to and reading from a file."""
    handler = fileHandler(filename=temp_file, right='w')
    handler.write("Hello, World!")
    handler.close()

    with open(temp_file, 'r') as f:
        content = f.read()
    assert content == "Hello, World!"

def test_fileHandler_safe_mode(temp_file):
    """Test safe mode to avoid overwriting files."""
    handler = fileHandler(filename=temp_file, right='w')
    handler.write("Initial content")
    handler.close()

    with pytest.raises(Exception):
        fileHandler(filename=temp_file, right='w', safeMode=True)

def test_fileHandler_append_mode(temp_file):
    """Test appending to an existing file."""
    handler = fileHandler(filename=temp_file, right='w')
    handler.write("First line\n")
    handler.close()

    handler = fileHandler(filename=temp_file, append=True)
    handler.write("Second line\n")
    handler.close()

    with open(temp_file, 'r') as f:
        content = f.readlines()
    assert content == ["First line\n", "Second line\n"]

def test_fileHandler_compression_gz(tmp_path):
    """Test writing to a gzip-compressed file."""
    gz_file = tmp_path / "test_file.txt.gz"
    handler = fileHandler(filename=gz_file, right='wt', gz=True)
    handler.write("Compressed content")
    handler.close()

    with gzip.open(gz_file, 'rt') as f:
        content = f.read()
    assert content == "Compressed content"

def test_fileHandler_compression_bz2(tmp_path):
    """Test writing to a bzip2-compressed file."""
    bz2_file = tmp_path / "test_file.txt.bz2"
    handler = fileHandler(filename=bz2_file, right='wt', bz2=True)
    handler.write("Compressed content")
    handler.close()

    with bz2.open(bz2_file, 'rt') as f:
        content = f.read()
    assert content == "Compressed content"

def test_fileHandler_close(temp_file):
    """Test closing the file."""
    handler = fileHandler(filename=temp_file, right='w')
    handler.write("Some content")
    handler.close()
    assert handler.fhandle is None