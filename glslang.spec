# (akien) No soname upstream, arbitrarily using 0 for now
# Without proper soname, the devel package would not generate the
# devel() provides that RPM relies on to pull in the proper deps
# in reverse dependencies.
%define major 11
%define libname %mklibname %{name} %{major}
%define devname %mklibname %{name} -d

# Cyclic dependencies between HLSL and glslang, we can't build with --no-undefined
# for the time being: https://github.com/KhronosGroup/glslang/issues/1484
%define _disable_ld_no_undefined 1

Name:		glslang
Version:	11.8.0
Release:	1
Summary:	Khronos reference front-end for GLSL and ESSL, and sample SPIR-V generator
Group:		System/Libraries
License:	BSD and GPLv3+ and ASL 2.0
URL:		https://github.com/KhronosGroup
Source0:	%url/%{name}/archive/%{version}/%{name}-%{version}.tar.gz
Patch1:		glslang-default-resource-limits_staticlib.patch
Patch2:		glslang_tests.patch
# Patch to build against system spirv-tools
Patch3:		0001-pkg-config-compatibility.patch
Patch4:		glslang-soversions-for-all-libraries.patch

BuildRequires:	cmake
BuildRequires:	pkgconfig(SPIRV-Tools)

%description
%{name} is the official reference compiler front end for the OpenGL
ES and OpenGL shading languages. It implements a strict
interpretation of the specifications for these languages.

%package -n %{libname}
Summary:	Library files for glslang
Group:		System/Libraries

%description -n %{libname}
Library files for glslang.

%package -n %{devname}
Summary:	Development files for glslang
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{devname}
%{name} is the official reference compiler front end for the OpenGL
ES and OpenGL shading languages. It implements a strict
interpretation of the specifications for these languages.

%prep
%autosetup -p1
# Fix rpmlint warning on debuginfo
find . -name '*.h' -or -name '*.cpp' -or -name '*.hpp'| xargs chmod a-x

%build
%cmake \
  -DGLSLANG_SOVERSION=%{major} \
  -DGLSLANG_VERSION=%{version}

%make_build

%install
%make_install -C build

# For compatibility with old versions
ln -s %{name}/SPIRV %{buildroot}%{_includedir}/

# Not needed, linked into the shared libs
rm -f %{buildroot}%{_libdir}/*.a

%check
pushd Test
LD_LIBRARY_PATH+=%{buildroot}%{_libdir} ./runtests
popd

%files
%doc README.md README-spirv-remap.txt
%{_bindir}/glslangValidator
%{_bindir}/spirv-remap

%files -n %{libname}
%{_libdir}/lib%{name}*.so.%{major}*
%{_libdir}/libHLSL.so.%{major}*
%{_libdir}/libSPIRV.so.%{major}*
%{_libdir}/libSPVRemapper.so.%{major}*

%files -n %{devname}
%{_includedir}/SPIRV
%{_includedir}/%{name}/
%{_libdir}/lib%{name}*.so
%{_libdir}/libHLSL.so
%{_libdir}/libSPIRV.so
%{_libdir}/libSPVRemapper.so
%{_libdir}/pkgconfig/glslang.pc
%{_libdir}/pkgconfig/spirv.pc
%{_libdir}/cmake/*.cmake
