# Managing Lasair Assets with Gulp

## TL;DR

Just do this:

```bash
sudo apt install nodejs
sudo apt install npm
sudo npm install --global gulp-cli
cd ~/lasair4/webserver/staticfiles/
npm install
gulp build
cd ..
export PYTHONPATH="$PYTHONPATH:/home/ubuntu/lasair-lsst/common/"
python3 manage.py collectstatic --settings lasair.settings
```

## Extra Installs Needed for a Fresh Dev Build

```bash
sudo apt install nodejs
sudo apt install npm
sudo npm install --global gulp-cli
```

## Gulp Build

Vendor Javascript and CSS codes can typically be installed and managed with the Node Package Manager. Node and NPM are quick to install (see here for [Ubuntu install instructions](https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-ubuntu-20-04).)

We then use Gulp to automate several tasks when it comes bundling out web assets (compile SCSS to CSS, combine and minify CSS and JS). Gulp is also easy to install (`npm install --global gulp-cli`).

To build the static assets simply:

```bash
cd ~/lasair4/webserver/staticfiles/
npm install
gulp build
cd ..
python3 manage.py collectstatic --settings lasair.settings
```

Gulp bundles all assets into `staticfiles/build` which can then be picked up by Django `collectstatic` command.

## Adding Node Modules (like pip install for web assets)

If the node module can be found in the node package manager (NPM), and most can, then follow this checklist. We will use `plotly.js` as our example:

* Add the module to `package.json` dependencies and include the minimum version number (look it up on [npm](https://www.npmjs.com/package/plotly.js)).

```bash
"dependencies": {
        ...
        "plotly.js": "^2.14.0",
        ...
},
```

* Now run `npm install` to add the module to the `node_modules` directory in staticfiles.
* In the `gulp.js` `concat:vendor:js` task add the path to the JS file of the package (and CSS to the `concat:vendor:css` task if needed).


```bash
// CONCAT AND MINIFY VENDOR JS - MAKE SURE ORDER IS CORRECT FOR DEPENDENCIES
gulp.task('concat:vendor:js', function() {
    return gulp.src([
            ...
            paths.src.node_modules + '/plotly.js/dist/plotly.min.js',
            ...

});
```

* Run `gulp build`

## Adding Other Vendor Web Assets (not available as Node Modules)

To add a minified CSS or JS file that is not installed from npm, download it to the `vendor` folder of `staticfiles`. Then add it to the `concat:vendor:css` and `concat:vendor:js` tasks in `gulpfile.js`. Keep the JS files in dependency order (for example, a jQuery plugin must come after `jquery`).

* Run `gulp build`

## Aladin Lite

Lasair serves its own copy of Aladin Lite. It does not load it from the CDS servers, because a slow CDS response used to block every page. The file lives in a folder named after its version, in two places:

* `staticfiles/vendor/aladin-lite/<VERSION>/aladin.js`, which `gulp build` copies (task `copy:dist:vendor`)
* `static/vendor/aladin-lite/<VERSION>/aladin.js`, which is committed and served in production

Aladin Lite is not on any page by default. A template that shows a sky map includes `includes/aladin_loader.html`, then calls `loadAladin(ALADIN_SRC, '#container-id').then(...)` instead of `A.init.then(...)`. `loadAladin` (in `src/js/lasair_aladin.js`) imports the file in the background. If Aladin Lite does not load within 10 seconds, it shows a message in the container that asks the user to reload, and the rest of the page keeps working. Templates that use it today: `index.html`, `includes/widgets/widget_mma_watchmap_header.html` and `includes/widgets/widget_object_aladin.script` (object page).

To upgrade Aladin Lite, take the `dist/aladin.js` file from the npm package. It is an ES module with the WebAssembly code included, so no other file is needed:

```bash
VERSION=3.8.1
curl -sL "https://registry.npmjs.org/aladin-lite/-/aladin-lite-${VERSION}.tgz" | tar -xz
mkdir -p vendor/aladin-lite/${VERSION} ../static/vendor/aladin-lite/${VERSION}
cp package/dist/aladin.js package/LICENSE vendor/aladin-lite/${VERSION}/
cp package/dist/aladin.js package/LICENSE ../static/vendor/aladin-lite/${VERSION}/
rm -rf package
```

Then change the version in `ALADIN_SRC` in `webserver/lasair/templates/includes/aladin_loader.html`, and check the home page and an MMA watchmap page.
