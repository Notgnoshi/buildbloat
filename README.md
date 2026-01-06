# buildbloat2

An updated version of https://github.com/nico/buildbloat targeting
https://github.com/Notgnoshi/webtreemap v2.

## How to use

Install https://github.com/Notgnoshi/webtreemap

```sh
git clone https://github.com/Notgnoshi/webtreemap.git
cd webtreemap
# Install the dependencies
npm install
# Make the script globally available
npm link
```

Do a clean build of your project with Ninja. If you're using https://ccache.dev/ disable it for this
build:

```sh
rm -rf ./build/
export CCACHE_DISABLE=1
cmake -B ./build/ -G Ninja
cmake --build ./build/ --parallel
```

Then run buildbloat on the normalized log file:

> [!WARNING]
>
> The `.ninja_log` targets can contain a mix of absolute and relative paths; they're all supposed to
> be artifacts in the build directory, but it is helpful to normalize them all to be relative to the
> build directory. This is what the `buildbloat.py --build-dir <DIR>` option does.

```sh
./buildbloat.py --build-dir ../project/build/ | webtreemap -o project-bloat.html
xdg-open project-bloat.html
```
