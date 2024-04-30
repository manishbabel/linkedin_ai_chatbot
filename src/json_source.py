import datetime
import json
from pathlib import Path
from typing import Iterable

from bytewax.inputs import DynamicSource, StatelessSourcePartition


def json_generator(json_files: list[Path]) -> Iterable[dict]:
    for json_file in json_files:
        with json_file.open() as file:
            data = json.load(file)
        yield list(data["Posts"].items())
        

class JSONPartition(StatelessSourcePartition):
    def __init__(self, json_files: list[str]) -> None:
        json_files = [Path(json_file) for json_file in json_files]
        self._generator = json_generator(json_files=json_files)

    def next_batch(self,_sched: datetime) -> Iterable[dict]:
        while True:
            return next(self._generator)
        
class JSONSource(DynamicSource):
    def __init__(self,json_files:list[str]):
        self._json_files = json_files

    def build(
            self,now:datetime, worker_index: int , worker_count:int
    ) -> JSONPartition:
        num_files_per_worker = len(self._json_files)
        num_leftover_files = num_files_per_worker % worker_count
        start_index = worker_index * num_files_per_worker
        end_index = start_index + num_files_per_worker
        if worker_index == worker_count - 1:
            end_index += num_leftover_files

        return JSONPartition(self._json_files[start_index:end_index])
        