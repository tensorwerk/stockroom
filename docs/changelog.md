# Changelog

All notable changes to this project will be documented here

The format is a modified version based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)


## In Progress

* [**Breaking Change**] `.keys()` returns relevant keys. This change breaks the model storage APIs [#35](https://github.com/tensorwerk/stockroom/pull/35) [@hhsecond](https://github.com/hhecond)

* [Rich](https://rich.readthedocs.io/en/latest/) based console [#32](https://github.com/tensorwerk/stockroom/pull/32) [@jjmachan](https://github.com/jjmachan) 

#### Fixed

* Structural change and shape error fix in `import` utility [#27](https://github.com/tensorwerk/stockroom/pull/27) [@jjmachan](https://github.com/jjmachan)

## 0.2.2
2020-08-06

#### Fixed

* Import error on `make_torch_dataset` with hangar's old version [#26](https://github.com/tensorwerk/stockroom/pull/26) [@hhsecond](https://github.com/hhecond)


## 0.2.1
2020-08-06


#### Added

* The `import` CLI for importing PyTorch datasets (torchvision, torchtext and torchaudio) [#17](https://github.com/tensorwerk/stockroom/pull/17) [@jjmachan](https://github.com/jjmachan)


#### Changed

* Hangar's new column API [#12](https://github.com/tensorwerk/stockroom/pull/12) [@hhsecond](https://github.com/hhecond)

* Global read optimization [#11](https://github.com/tensorwerk/stockroom/pull/11) [@hhsecond](https://github.com/hhecond)

* Singleton for holding the checkout object has been removed [#3](https://github.com/tensorwerk/stockroom/pull/3) [@hhsecond](https://github.com/hhecond)


## 0.1.0
2019-12-12

* First release on PyPI
