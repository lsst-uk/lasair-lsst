# Managing Lasair Assets with Gulp

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

Using Aladin-lite as an example, which is not currently available as a node module, we need to include the minified CSS and JS files. We first download these to the `vendor` folder of our `staticfiles`.

```bash
cd ~/lasair4/webserver/staticfiles/vendor
curl "https://aladin.u-strasbg.fr/AladinLite/api/v2/latest/aladin.min.css" -o aladin.min.css
curl "https://aladin.u-strasbg.fr/AladinLite/api/v2/latest/aladin.min.js" -o aladin.min.js
```

Now add these files to the `concat:vendor:css` and `concat:vendor:js` tasks in the `gulp.js` file making sure to get the order of the js files correct (for example `aladin.min.js` needs to come after `jquery`).

* Run `gulp build`
