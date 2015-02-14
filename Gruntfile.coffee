module.exports = (grunt) ->
  grunt.initConfig
    pkg: grunt.file.readJSON('package.json')
    sass:
      options:
        sourceMap: true
      dist:
        files:
          'example_project/static/css/tx_lobbying.css': 'example_project/static/sass/tx_lobbying.sass'
    autoprefixer:
      options:
        browsers: ['last 3 versions', 'ie 8']
        diff: true
        map: true
        single_file:
          src: 'example_project/static/css/tx_lobbying.css'
          # overwrite original
          dest: 'example_project/static/css/tx_lobbying.css'
    jshint:
      all: [
        'example_project/static/js_src/**/*.js'
      ]
    browserify:
      app:
        files:
          'example_project/static/js/tx_lobbying.js': 'example_project/static/js_src/main.js'
    uglify:
      app:
        files:
          'example_project/static/js/tx_lobbying.min.js': ['example_project/static/js/tx_lobbying.js']
    watch:
      # use live reload if the browser has it
      # if you don't have it you can get it here:
      # http://feedback.livereload.com/knowledgebase/articles/86242-how-do-i-install-and-use-the-browser-extensions-
      options:
        livereload: true
      sass:
        files: ['example_project/static/sass/**/*.sass']
        tasks: ['sass', 'autoprefixer']
        options:
          livereload: false
          # spawn has to be on or else the css watch won't catch changes
          spawn: true
      css:
        files: ['example_project/static/css/**/*.css']
        options:
          spawn: false
      scripts:
        files: ['example_project/static/js_src/**/*.js']
        tasks: ['browserify', 'uglify']
        options:
          spawn: false

  grunt.loadNpmTasks 'grunt-sass'
  grunt.loadNpmTasks 'grunt-autoprefixer'
  grunt.loadNpmTasks 'grunt-contrib-jshint'
  grunt.loadNpmTasks 'grunt-browserify'
  grunt.loadNpmTasks 'grunt-contrib-uglify'
  grunt.loadNpmTasks 'grunt-contrib-watch'

  # build the assets needed
  grunt.registerTask('build', ['sass', 'autoprefixer', 'browserify', 'uglify'])
  # build the assets with sanity checks
  grunt.registerTask('default', ['sass', 'autoprefixer', 'jshint', 'browserify', 'uglify'])
  # build assets and automatically re-build when a file changes
  grunt.registerTask('dev', ['build', 'watch'])
