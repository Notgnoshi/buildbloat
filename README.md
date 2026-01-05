# buildbloat2

An updated version of https://github.com/nico/buildbloat targeting
https://github.com/evmar/webtreemap v2.

## How to use

Install https://github.com/evmar/webtreemap

```sh
npm install -g webtreemap
```

Do a clean build of your project with Ninja. If you're using https://ccache.dev/ disable it for this
build:

```sh
rm -rf ./build/
export CCACHE_DISABLE=1
cmake -B ./build/ -G Ninja
cmake --build ./build/ --parallel
```

Then run buildbloat on the resulting `.ninja_log` file:

```sh
./buildbloat.py ./build/.ninja_log | webtreemap -o buildbloat.html
xdg-open buildbloat.html
```
