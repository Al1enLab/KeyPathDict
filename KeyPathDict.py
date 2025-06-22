'''
Librairie de manipulation d'un dictionnaire imbriqué via des chemins de clés
Permet d'accéder à des dictionnaires imbriqués via des KeyPath, à savoir des chemins
de clés sous forme de tuples.
'''
from typing import Any, Hashable, Mapping, Self

class KeyPath(tuple):
    '''Représentation d'un chemin de clés'''
    
    @property
    def descendants(self) -> "KeyPath":
        '''Retourne les éléments du KeyPath à l'exception du premier'''
        return __class__(self[1:])
    
    @property
    def top(self) -> Hashable:
        '''Retourne le premier élément du KeyPath'''
        return self[0]
    
    @property
    def length(self) -> int:
        '''Retourne la longueur du KeyPath'''
        return len(self)

    def __add__(self, element: Any) -> "KeyPath":
        '''Addition de KeyPaths
        KeyPath(['a', 'b', 'c']) + KeyPath(['d', 'e', 'f']) = KeyPath(['a', 'b', 'c', 'd', 'e', 'f'])'''
        if isinstance(element, __class__):
            return __class__(list(self) + list(element))
        return __class__(list(self) + [ element ])
    
    def __repr__(self):
        return f'<{__class__.__name__} ({str(self)})>'
    
    def __str__(self):
        return '.'.join(map(str, self))
    
class KeyPathDict(dict):
    
    def __init__(self, *args, recursive_create: bool = True, **kwargs) -> None:
        '''
        recursive_create : si True, __set__ crée chaque élément du KeyPath si celui-ci n'existe pas
        '''
        self.recursive_create = recursive_create
        super().__init__(*args, **kwargs)
    
    def _recursive_get(self, keypath: KeyPath, _subdict: Mapping=None, _thispath: KeyPath=None, _fullpath: KeyPath=None) -> Any:
        '''Retourne la valeur de la clé en fin de KeyPath'''
        if _subdict is None:
            _subdict = self
        if _thispath is None:
            _thispath = KeyPath()
        if _fullpath is None:
            _fullpath = keypath
        
        # Si le KeyPath ne comporte qu'une seule cle, on retourne la valeu de cette clé si elle existe
        if len(keypath) == 1:
            try:
                return _subdict[keypath.top]
            except KeyError:
                raise KeyError(f'{repr(_thispath + keypath.top)} (from {repr(_fullpath)})')
            
        # Sinon on retourne le sous-dictionnaire de la première clé du keypath, s'il existe
        else:
            try:
                _subdict = _subdict[keypath.top]
            except KeyError:
                raise KeyError(f'{repr(_thispath + keypath.top)} (from {repr(_fullpath)})')
            if not isinstance(_subdict, Mapping):
                raise TypeError(f'KeyPath {repr(_thispath + keypath.top)} (from {repr(_fullpath)}) entry is not a mapping')
            else:
                return self._recursive_get(keypath=keypath.descendants, _subdict=_subdict, _thispath=_thispath + keypath.top, _fullpath=_fullpath)

            
    def _recursive_set(self, keypath: KeyPath, value: Any, _fullpath: KeyPath=None, _subdict: dict=None) -> None:
        '''Affecte value à la clé en fin du KeyPath'''
        if _subdict is None:
            _subdict = self
        if _fullpath is None:
            _fullpath = keypath

        if keypath.length == 1:
            _subdict[keypath.top] = value
        else:
            if keypath.top not in _subdict:
                if not self.recursive_create:
                    raise KeyError(_fullpath)
                _subdict[keypath.top] = { }
            
            if not isinstance(_subdict[keypath.top], Mapping) :
                _subdict[keypath.top] = { }

            self._recursive_set(keypath=keypath.descendants, value=value, _fullpath=_fullpath, _subdict=_subdict[keypath.top])
        
    def __getitem__(self, key) -> Any:
        '''Comme l'original, avec prise en charge de KeyPath'''
        if not isinstance(key, KeyPath):
            return super().__getitem__(key)
        else:
            return self._recursive_get(keypath=key)

    def __setitem__(self, key: Hashable, value):
        '''Comme l'original, avec prise en charge de KeyPath'''
        if not isinstance(key, KeyPath):
            return super().__setitem__(key, value)
        else:
            return self._recursive_set(keypath=key, value=value)
    
    def kpitems(self, depth: int=None, _path: list=[ ], _subdict: dict=None) -> tuple:
        '''Comme .items(), mais retourne des KeyPath en guise de clés'''
        if _subdict is None:
            _subdict = self
        path = list(_path)
        for key, value in _subdict.items():
            if isinstance(value, Mapping):
                if depth == 0:
                    yield KeyPath(path + [ key ]), value
                else:
                    if depth is not None:
                        depth -= 1
                    yield from self.kpitems(depth, path + [ key ], _subdict=_subdict[key])
            else:
                yield KeyPath(path + [ key ]), value 

    def get(self, key: Hashable, default: Any=None) -> Any:
        ''' Comme .get, mais avec prise en charge d'un KeyPath'''
        try:
            return self.__getitem__(key)
        except KeyError:
            return default
    
    def merge(self, other_dict: Mapping, depth: int=None) -> Self:
        '''Fusionne le KeyPathDict avec le dictionnaire other_dict jusqu'à la profondeur depth'''
        for keypath, value in __class__(other_dict).kpitems(depth=depth):
            self[keypath] = value
        return self

    def deepcopy(self):
        '''Retourne une copie complète du KeyPath'''
        output = __class__()
        for keypath, value in self.kpitems():
            output[keypath] = value
        return output
