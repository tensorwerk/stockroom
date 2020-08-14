If you wish to contribute to stockroom (yaay!!🎉🎉) decide whether it needs to be discussed with the dev team
before you start spending time on it. If you are in doubt, ask us in [slack](https://join.slack.com/t/hangarusergroup/shared_invite/zt-886tggtd-_rs1RIb5ACz5g~AzyhphPg)
or raise a [Github issue](https://github.com/tensorwerk/stockroom/issues/new/choose) (🙄) 


- You'd need to fork the stockroom repository (look for the "Fork" button on top right) and then clone the fork locally.

```bash
git clone git@github.com:your_name_here/stockroom.git
```

- Create a branch locally and make your changes. Feel free to reach us if you need a code review before you finish your work

```bash
git checkout -b your-branch-name
```

## Contributing to the code

Once done with the changes, run the test suite. It will run existing test cases, check coverage, run `black` and `mypy`.
Also, make sure you have updated the documentation, added required test cases and modified the `changelog.md` file
in `docs` directory before creating the PR

<div class="termy">

```console
$ bash ./scripts/test.sh
---> 100%
```

</div>

## Contributing to the documentation

We are using the amazing [mkdocs](https://www.mkdocs.org/) library for documentation. You can spin up the mkdocs live debugging server
from the root of the repository and see the changes you are making in realtime. 


<div class="termy">

```console
$ mkdocs serve
---> 100%
```

</div>
