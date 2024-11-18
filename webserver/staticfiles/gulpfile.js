/*

=========================================================
* Volt Free - Bootstrap 5 Dashboard
=========================================================

* Product Page: https://themesberg.com/product/admin-dashboard/volt-premium-bootstrap-5-dashboard
* Copyright 2020 Themesberg (https://www.themesberg.com)
* License (https://themesberg.com/licensing)

* Designed and coded by https://themesberg.com

=========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. Please contact us to request a removal.

*/

var autoprefixer = require('gulp-autoprefixer');
var browserSync = require('browser-sync').create();
var cleanCss = require('gulp-clean-css');
var del = require('del');
const htmlmin = require('gulp-htmlmin');
const cssbeautify = require('gulp-cssbeautify');
var gulp = require('gulp');
const npmDist = require('gulp-npm-dist');
var sass = require('gulp-sass')(require('sass'));
var wait = require('gulp-wait');
var sourcemaps = require('gulp-sourcemaps');
var fileinclude = require('gulp-file-include');
var concat = require('gulp-concat');
var rename = require('gulp-rename');
var uglify = require('gulp-uglify');
var touch = require('gulp-touch-fd');

// Define paths

const paths = {
    dist: {
        base: './build/',
        css: './build/css',
        js: './build/js',
        files: './build/files',
        img: './build/img',
        vendor: './build/vendor',
        fonts: './build/webfonts'
    },
    base: {
        base: './',
        node: './node_modules',
        scss: './scss',
        js: './js',
        img: './img',
        files: './files',
    },
    src: {
        base: './src/',
        css: './src/css',
        files: './src/files/**/*.*',
        img: './src/img/**/*.*',
        js: './src/js',
        js2: './src/js/**/*.*',
        scss: './src/scss',
        node_modules: './node_modules',
        vendor: './vendor',
        fonts: './src/webfonts/**/*.*'
    },
};

// Compile SCSS
gulp.task('scss', function() {
    return gulp.src([paths.src.scss + '/custom/**/*.scss', paths.src.scss + '/volt/**/*.scss', paths.src.scss + '/volt.scss'])
        .pipe(wait(500))
        .pipe(sourcemaps.init())
        .pipe(sass().on('error', sass.logError))
        .pipe(autoprefixer({
            overrideBrowserslist: ['> 1%']
        }))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(paths.temp.css))
        .pipe(touch())
        .pipe(browserSync.stream());

});

// MOVE FILES AND IMAGES
gulp.task('assets', function() {
    return gulp.src([paths.src.assets])
        .pipe(gulp.dest(paths.temp.assets))
        .pipe(browserSync.stream());
});

// MOVE NODE MODULES TO VENDOR
gulp.task('vendor', function() {
    return gulp.src(npmDist(), {
            base: paths.src.node_modules
        })
        .pipe(gulp.dest(paths.temp.vendor));
});

// Beautify CSS
gulp.task('beautify:css', function() {
    return gulp.src([
            paths.dist.css + '/volt.css'
        ])
        .pipe(cssbeautify())
        .pipe(gulp.dest(paths.dist.css))
        .pipe(touch())
});

// MINIFY CSS
gulp.task('minify:css', function() {
    return gulp.src([
            paths.dist.css + '/volt.css'
        ])
        .pipe(cleanCss())
        .pipe(gulp.dest(paths.dist.css))
        .pipe(touch())
});

// CONCAT AND MINIFY VENDOR CSS
gulp.task('concat:vendor:css', function() {
    return gulp.src([
            paths.src.node_modules + '/@fortawesome/fontawesome-free/css/all.min.css',
            paths.src.node_modules + '/sweetalert2/dist/sweetalert2.min.css',
            paths.src.node_modules + '/notyf/notyf.min.css',
            paths.src.node_modules + '/js9/js9support.css',
            paths.src.node_modules + '/js9/js9.css',
            paths.src.node_modules + '/tributejs/dist/tribute.css',
            //paths.src.vendor + '/aladin.min.css',
            paths.src.vendor + '/prism.css',
            paths.src.vendor + '/prism-live.css',
            paths.src.vendor + '/style.css',

        ])
        .pipe(sourcemaps.init())
        .pipe(cleanCss())
        .pipe(concat('vendor.css'))
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(paths.dist.css))
        .pipe(touch())
});

// CONCAT AND MINIFY LASAIR JS
gulp.task('concat:dist:js', function() {
    return gulp.src([
            paths.src.js + '/volt.js',
            paths.src.js + '/lasair_datatables.js',
            paths.src.js + '/lasair_js9.js',
            paths.src.js + '/fitsview_init.js',
            paths.src.js + '/fitsview.js',
            paths.src.js + '/lasair_utils.js',
            paths.src.js + '/lasair_fixes.js',
        ])
        .pipe(sourcemaps.init())
        .pipe(concat('main.js'))
        .pipe(uglify())
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(paths.dist.js))
        .pipe(touch())
});

// CONCAT AND MINIFY VENDOR JS - MAKE SURE ORDER IS CORRECT FOR DEPENDENCIES
gulp.task('concat:vendor:js', function() {
    return gulp.src([
            paths.src.node_modules + '/@popperjs/core/dist/umd/popper.min.js',
            paths.src.node_modules + '/bootstrap/dist/js/bootstrap.min.js',
            paths.src.node_modules + '/onscreen/dist/on-screen.umd.min.js',
            paths.src.node_modules + '/nouislider/dist/nouislider.min.js',
            paths.src.node_modules + '/smooth-scroll/dist/smooth-scroll.polyfills.min.js',
            paths.src.node_modules + '/chartist/dist/chartist.min.js',
            paths.src.node_modules + '/chartist-plugin-tooltips/dist/chartist-plugin-tooltip.min.js',
            paths.src.node_modules + '/vanillajs-datepicker/dist/js/datepicker.min.js',
            paths.src.node_modules + '/sweetalert2/dist/sweetalert2.all.min.js',
            paths.src.node_modules + '/moment/min/moment.min.js',
            paths.src.node_modules + '/vanillajs-datepicker/dist/js/datepicker.min.js',
            paths.src.node_modules + '/notyf/notyf.min.js',
            paths.src.node_modules + '/simplebar/dist/simplebar.min.js',
            paths.src.node_modules + '/tributejs/dist/tribute.js',
            paths.src.node_modules + '/@fortawesome/fontawesome-free/js/all.min.js',
            paths.src.node_modules + '/simple-datatables/dist/umd/simple-datatables.js',
            paths.src.node_modules + '/plotly.js/dist/plotly.min.js',
            paths.src.node_modules + '/jquery/dist/jquery.min.js',
            paths.src.vendor + '/prism.js',
            paths.src.vendor + '/prism-live.js',

        ])
        .pipe(sourcemaps.init())
        .pipe(concat('vendor.js'))
        .pipe(uglify())
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(paths.dist.js))
        .pipe(touch())
});

// Clean
gulp.task('clean:dist', function() {
    return del([paths.dist.base]);
});

// Compile and copy scss/css
gulp.task('copy:dist:css', function() {
    return gulp.src([paths.src.scss + '/volt/**/*.scss', paths.src.scss + '/custom/_variables.scss', paths.src.scss + '/custom/_custom.scss', paths.src.scss + '/custom/**/*.scss', paths.src.scss + '/volt.scss'])
        .pipe(wait(500))
        .pipe(sourcemaps.init())
        .pipe(sass().on('error', sass.logError))
        .pipe(autoprefixer({
            overrideBrowserslist: ['> 1%']
        }))
        .pipe(rename('main.css'))
        .pipe(cleanCss())
        .pipe(sourcemaps.write('.'))
        .pipe(gulp.dest(paths.dist.css))
        .pipe(touch())
});

// COPY FILES
gulp.task('copy:dist:files', function() {
    return gulp.src(paths.src.files)
        .pipe(gulp.dest(paths.dist.files))
});

// COPY FONTS
gulp.task('copy:dist:fonts', function() {
    return gulp.src(paths.src.fonts)
        .pipe(gulp.dest(paths.dist.fonts))
});

// COPY IMAGES
gulp.task('copy:dist:img', function() {
    return gulp.src(paths.src.img)
        .pipe(gulp.dest(paths.dist.img))
});

// COPY JS
gulp.task('copy:dist:js', function() {
    return gulp.src(paths.src.js2)
        .pipe(gulp.dest(paths.dist.js))
});

// COPY REQUIRED VENDOR MODULES
gulp.task('copy:dist:vendor', function() {
    gulp.src(paths.src.node_modules + '/bootstrap-multiselect/dist/**/*.*', )
        .pipe(gulp.dest(paths.dist.vendor + "/bootstrap-multiselect"))
    return gulp.src(paths.src.node_modules + '/js9/**/*.*', )
        .pipe(gulp.dest(paths.dist.vendor + "/js9"))
});

gulp.task('serve', gulp.series('copy:dist:css', 'copy:dist:files', 'copy:dist:fonts', 'copy:dist:img', 'concat:dist:js', function() {
    gulp.watch([paths.src.scss + '/volt/**/*.scss', paths.src.scss + '/custom/_variables.scss', paths.src.scss + '/custom/*.scss', paths.src.scss + '/custom/**/*.scss', paths.src.scss + '/volt.scss'], gulp.series('copy:dist:css'));
    gulp.watch([paths.src.files], gulp.series('copy:dist:files'));
    gulp.watch([paths.src.fonts], gulp.series('copy:dist:fonts'));
    gulp.watch([paths.src.img], gulp.series('copy:dist:img'));
    gulp.watch([paths.src.js], gulp.series('concat:dist:js'));
}));

gulp.task('build', gulp.series('clean:dist', 'copy:dist:css', 'copy:dist:files', 'copy:dist:fonts', 'copy:dist:img', 'copy:dist:js', 'concat:dist:js', 'concat:vendor:js', 'concat:vendor:css', 'copy:dist:vendor'));

// Default
gulp.task('default', gulp.series('serve'));
