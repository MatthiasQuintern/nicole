# Maintainer: Matthias Quintern <matthias(dot)quintern(at)posteo(dot)de>
pkgname=nicole
pkgver=2.1.0
pkgrel=1
pkgdesc="Write lyrics from genius or azlyrics.com to a mp3-tag"
arch=('any')
url="https:/github.com/MatthiasQuintern/nicole"
license=('GPL3')
depends=('python-mutagen' 'python-beautifulsoup4')
source=(file://${PWD}/nicole/nicole.py _nicole.compdef.zsh nicole.1.man)
md5sums=('1cfc6bca38b8e1b8c28694226eebb31e'
         'a0a390f36de74a366065ab65bfd1d8de'
         '4ad29357b608c88eebc49546a50e489d')

package() {
	mkdir -p "${pkgdir}/usr/bin"
	cp "${srcdir}/nicole.py" "${pkgdir}/usr/bin/nicole"
	chmod +x "${pkgdir}/usr/bin/nicole"

	mkdir -p "${pkgdir}/usr/share/man/man1/"
	cp "${srcdir}/nicole.1.man" "${pkgdir}/usr/share/man/man1/nicole.1"

	# if zsh is installed
	if [[ -f /bin/zsh ]]; then
		mkdir -p "${pkgdir}/usr/share/zsh/site-functions"
		cp "${srcdir}/_nicole.compdef.zsh" "${pkgdir}/usr/share/zsh/site-functions/_nicole"
		chmod +x "${pkgdir}/usr/share/zsh/site-functions/_nicole"
	fi
}
