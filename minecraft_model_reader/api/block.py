from typing import Dict, Union, Tuple
import copy
import re


class Block:
	"""
	A minified version of the block class from the Amulet Editor.
	"""

	blockstate_regex = re.compile(
		r"(?:(?P<namespace>[a-z0-9_.-]+):)?(?P<base_name>[a-z0-9/._-]+)(?:\[(?P<property_name>[a-z0-9_]+)=(?P<property_value>[a-z0-9_]+)(?P<properties>.*)\])?"
	)

	parameters_regex = re.compile(r"(?:,(?P<name>[a-z0-9_]+)=(?P<value>[a-z0-9_]+))")

	def __init__(self, blockstate: str = None, namespace: str = None, base_name: str = None, properties: Dict[str, Union[str, bool, int]] = None):
		self._blockstate = blockstate
		self._namespace = namespace
		self._base_name = base_name

		if namespace is not None and base_name is not None and properties is None:
			properties = {}

		self._properties = properties

	@property
	def namespace(self) -> str:
		return self._namespace

	@property
	def base_name(self) -> str:
		return self._base_name

	@property
	def properties(self) -> Dict[str, Union[str, bool, int]]:
		return copy.deepcopy(self._properties)

	@property
	def blockstate(self) -> str:
		if self._blockstate is None:
			self._gen_blockstate()
		return self._blockstate

	@property
	def blockstate_without_waterlogged(self):
		blockstate = f"{self.namespace}:{self.base_name}"
		if self.properties:
			props = [f"{key}={value}" for key, value in sorted(self.properties.items()) if key != 'waterlogged']
			blockstate = f"{blockstate}[{','.join(props)}]"
		return blockstate

	def _gen_blockstate(self):
		self._blockstate = f"{self.namespace}:{self.base_name}"
		if self.properties:
			props = [f"{key}={value}" for key, value in sorted(self.properties.items())]
			self._blockstate = f"{self._blockstate}[{','.join(props)}]"

	def __str__(self) -> str:
		"""
		:return: The base blockstate string of the Block object
		"""
		return self.blockstate

	def __eq__(self, other: 'Block') -> bool:
		if self.__class__ != other.__class__:
			return False

		return self.blockstate == other.blockstate

	def __hash__(self) -> int:
		return hash(self.blockstate)

	@staticmethod
	def parse_blockstate_string(blockstate: str) -> Tuple[str, str, Dict[str, str]]:
		match = Block.blockstate_regex.match(blockstate)
		namespace = match.group("namespace") or "minecraft"
		base_name = match.group("base_name")

		if match.group("property_name") is not None:
			properties = {match.group("property_name"): match.group("property_value")}
		else:
			properties = {}

		properties_string = match.group("properties")
		if properties_string is not None:
			properties_match = Block.parameters_regex.finditer(properties_string)
			for match in properties_match:
				properties[match.group("name")] = match.group("value")

		return namespace, base_name, {k: v for k, v in sorted(properties.items())}

	def uparse_blockstate_string(self):
		self._namespace, self._base_name, self._properties = self.parse_blockstate_string(
			self._blockstate
		)